import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";


import { AppHeader } from "../components/AppHeader";
import { DataStatePanel } from "../components/DataStatePanel";
import { cityService, municipalityService, newsService, projectService } from "../services/api";
import { AnnouncementItem, JobListingItem, MunicipalServiceItem, NewsItem, ProjectItem } from "../types";
import { borderRadius, colors, spacing, typography } from "../theme";
import { DataState, loadDataState, summarizeSources } from "../utils/dataState";
import { openExternalUrl } from "../utils/externalActions";

type IconName = keyof typeof Ionicons.glyphMap;
type OfficialFilter = "all" | "news" | "announcements" | "tenders" | "projects" | "jobs" | "services";
type FeedKind = "news" | "announcement" | "tender" | "project" | "job";
type MunicipalitySourceKey = "news" | "announcements" | "projects" | "jobs" | "services";
type MunicipalitySourceStates = Record<MunicipalitySourceKey, DataState<unknown>>;

type FeedItem = {
  id: string;
  kind: FeedKind;
  title: string;
  description?: string | null;
  date?: string | null;
  sourceUrl?: string | null;
  icon: IconName;
  accent: string;
  label: string;
  news?: NewsItem;
};

type MunicipalService = {
  id: string;
  title: string;
  description: string;
  icon: IconName;
  prompt: string;
  contact?: string | null;
  sourceUrl?: string | null;
};

const AUTO_REFRESH_MS = 10 * 60 * 1000;

const FILTERS: Array<{ key: OfficialFilter; label: string; icon: IconName }> = [
  { key: "all", label: "Tümü", icon: "pulse-outline" },
  { key: "news", label: "Haber", icon: "newspaper-outline" },
  { key: "announcements", label: "Duyuru", icon: "megaphone-outline" },
  { key: "tenders", label: "İhale", icon: "document-text-outline" },
  { key: "projects", label: "Proje", icon: "construct-outline" },
  { key: "jobs", label: "İş", icon: "briefcase-outline" },
  { key: "services", label: "Hizmet", icon: "grid-outline" },
];

const SERVICES: MunicipalService[] = [
  {
    id: "cozum",
    title: "Çözüm Merkezi",
    description: "Talep, şikayet ve başvuru yönlendirmesi.",
    icon: "chatbubbles-outline",
    prompt: "Aliağa Belediyesi çözüm merkezi, talep veya şikayet başvurusu için kullanıcıyı doğru kanala yönlendir.",
  },
  {
    id: "imar",
    title: "İmar ve Ruhsat",
    description: "İmar, yapı ruhsatı ve işyeri işlemleri.",
    icon: "business-outline",
    prompt: "Aliağa'da imar, ruhsat veya işyeri açma işlemleri için hangi belediye birimine başvurulur?",
  },
  {
    id: "sosyal",
    title: "Sosyal Destek",
    description: "Sosyal yardım ve destek hizmetleri.",
    icon: "heart-outline",
    prompt: "Aliağa Belediyesi sosyal destek ve yardım hizmetleri hakkında kullanıcıya özet bilgi ver.",
  },
  {
    id: "nikah",
    title: "Nikah İşlemleri",
    description: "Başvuru evrakları ve randevu akışı.",
    icon: "document-attach-outline",
    prompt: "Aliağa Belediyesi nikah işlemleri için gerekli adımları ve başvuru evraklarını anlat.",
  },
  {
    id: "vezne",
    title: "Vezne / Ödeme",
    description: "Vergi, harç ve ödeme işlemleri.",
    icon: "card-outline",
    prompt: "Aliağa Belediyesi vezne, vergi ve ödeme işlemleri hakkında kullanıcıyı yönlendir.",
  },
  {
    id: "cenaze",
    title: "Cenaze Hizmetleri",
    description: "Defin, nakil ve resmi süreç bilgisi.",
    icon: "flower-outline",
    prompt: "Aliağa'da belediye cenaze hizmetleri ve defin süreci için kullanıcıya resmi yönlendirme yap.",
  },
];

function normalizeText(value?: string | null): string {
  return (value || "")
    .toLocaleLowerCase("tr-TR")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ı/g, "i")
    .replace(/ğ/g, "g")
    .replace(/ş/g, "s")
    .replace(/ç/g, "c")
    .replace(/ö/g, "o")
    .replace(/ü/g, "u");
}

function cleanDisplayText(value?: string | null): string {
  return (value || "")
    .replace(/\s+/g, " ")
    .replace(/DEVAMINI OKU/gi, "")
    .replace(/\d{1,2}\s+(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)\s+\d{4}\s*\|\s*\d{1,2}:\d{2}/gi, "")
    .replace(/Aliağa Belediyesi İnsan Kaynakları ve Eğitim Müdürlüğü\s*©\s*\d{4}/gi, "")
    .trim();
}

function firstUsefulLine(value?: string | null): string {
  return (value || "")
    .split(/\n+/)
    .map(cleanDisplayText)
    .find((line) => line.length >= 12 && line.length <= 120) || "";
}

function conciseTitle(title?: string | null, fallback?: string | null): string {
  const cleaned = cleanDisplayText(title);
  const fallbackLine = firstUsefulLine(fallback);
  const source = cleaned.length > 120 && fallbackLine ? fallbackLine : cleaned || fallbackLine;
  return source.length > 126 ? `${source.slice(0, 123).trim()}...` : source || "Başlık bekleniyor";
}

function conciseDescription(value?: string | null): string | null {
  const cleaned = cleanDisplayText(value);
  if (!cleaned) return null;
  return cleaned.length > 190 ? `${cleaned.slice(0, 187).trim()}...` : cleaned;
}

function serviceIconFor(type?: string | null, title?: string | null): IconName {
  const text = normalizeText(`${type || ""} ${title || ""}`);
  if (text.includes("acil")) return "alert-circle-outline";
  if (text.includes("saglik") || text.includes("sağlık")) return "medical-outline";
  if (text.includes("altyapi") || text.includes("altyapı") || text.includes("su") || text.includes("elektrik")) return "flash-outline";
  if (text.includes("nikah")) return "document-attach-outline";
  if (text.includes("imar") || text.includes("ruhsat")) return "business-outline";
  if (text.includes("sosyal")) return "heart-outline";
  if (text.includes("vezne") || text.includes("odeme") || text.includes("ödeme")) return "card-outline";
  if (text.includes("cenaze")) return "flower-outline";
  if (text.includes("cozum") || text.includes("çözüm") || text.includes("153")) return "chatbubbles-outline";
  return "grid-outline";
}

function serviceCardFromDb(item: MunicipalServiceItem): MunicipalService {
  const hours = item.calisma_saatleri ? `Saat: ${item.calisma_saatleri}` : "Resmi hizmet kaydı";
  const contact = item.iletisim ? `İletişim: ${item.iletisim}` : null;
  return {
    id: `db-${item.id}`,
    title: item.birim,
    description: [hours, contact].filter(Boolean).join(" · "),
    icon: serviceIconFor(item.hizmet_tipi, item.birim),
    contact: item.iletisim,
    sourceUrl: item.source_url,
    prompt: `${item.birim} hakkında Aliağa Belediyesi resmi hizmet kaydına göre kullanıcıyı yönlendir. Hizmet tipi: ${item.hizmet_tipi}. İletişim: ${item.iletisim || "kayıt yok"}. Çalışma saatleri: ${item.calisma_saatleri || "kayıt yok"}.`,
  };
}

function isTender(item: AnnouncementItem): boolean {
  const type = normalizeText(item.type);
  return type.includes("ihale");
}

function formatDate(input?: string | null): string {
  if (!input) return "Tarih bekleniyor";
  const date = new Date(input);
  if (!Number.isFinite(date.getTime())) return "Tarih bekleniyor";
  return date.toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function dateValue(input?: string | null): number {
  if (!input) return 0;
  const value = new Date(input).getTime();
  return Number.isFinite(value) ? value : 0;
}

function itemDate(item: FeedItem): number {
  return dateValue(item.date);
}

function buildFeed(
  news: NewsItem[],
  announcements: AnnouncementItem[],
  projects: ProjectItem[],
  jobs: JobListingItem[]
): FeedItem[] {
  const newsItems = news.map((item): FeedItem => ({
    id: `news-${item.id}`,
    kind: "news",
    title: conciseTitle(item.title, item.content),
    description: conciseDescription(item.content),
    date: item.published_at || item.created_at,
    sourceUrl: item.source_url,
    icon: "newspaper-outline",
    accent: colors.info,
    label: "Haber",
    news: item,
  }));

  const announcementItems = announcements.map((item): FeedItem => {
    const tender = isTender(item);
    return {
      id: `${tender ? "tender" : "announcement"}-${item.id}`,
      kind: tender ? "tender" : "announcement",
      title: conciseTitle(item.title, item.content),
      description: conciseDescription(item.content),
      date: item.published_at || item.created_at,
      sourceUrl: item.source_url,
      icon: tender ? "document-text-outline" : "megaphone-outline",
      accent: tender ? colors.warning : colors.primary,
      label: tender ? "İhale" : "Duyuru",
    };
  });

  const projectItems = projects.map((item): FeedItem => ({
    id: `project-${item.id}`,
    kind: "project",
    title: conciseTitle(item.title, item.description),
    description: conciseDescription(item.description),
    date: item.created_at,
    sourceUrl: item.source_url,
    icon: "construct-outline",
    accent: colors.tertiary,
    label: item.status ? `Proje · ${item.status.replace(/_/g, " ")}` : "Proje",
  }));

  const jobItems = jobs.map((item): FeedItem => ({
    id: `job-${item.id}`,
    kind: "job",
    title: conciseTitle(item.title, item.description),
    description: conciseDescription([item.company, item.location, item.description].filter(Boolean).join(" · ")),
    date: item.published_at || item.created_at,
    sourceUrl: item.source_url,
    icon: "briefcase-outline",
    accent: colors.success,
    label: "İş İlanı",
  }));

  // Deduplicate items by kind and title (case-insensitive, space-ignored)
  const uniqueItems: FeedItem[] = [];
  const seenKeys = new Set<string>();
  const rawItems = [...newsItems, ...announcementItems, ...projectItems, ...jobItems];
  for (const item of rawItems) {
    const key = `${item.kind}_${(item.title || "").replace(/\s+/g, "").toLowerCase()}`;
    if (!seenKeys.has(key)) {
      seenKeys.add(key);
      uniqueItems.push(item);
    }
  }

  return uniqueItems.sort((a, b) => itemDate(b) - itemDate(a));
}

function filterFeed(feed: FeedItem[], selected: OfficialFilter): FeedItem[] {
  if (selected === "all") return feed.slice(0, 16);
  if (selected === "news") return feed.filter((item) => item.kind === "news");
  if (selected === "announcements") return feed.filter((item) => item.kind === "announcement");
  if (selected === "tenders") return feed.filter((item) => item.kind === "tender");
  if (selected === "projects") return feed.filter((item) => item.kind === "project");
  if (selected === "jobs") return feed.filter((item) => item.kind === "job");
  return [];
}

export function MunicipalityScreen() {
  const navigation = useNavigation<any>();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<OfficialFilter>("all");
  const [visibleLimit, setVisibleLimit] = useState<number>(6);
  const [sourceStates, setSourceStates] = useState<MunicipalitySourceStates | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [announcements, setAnnouncements] = useState<AnnouncementItem[]>([]);
  const [projects, setProjects] = useState<ProjectItem[]>([]);

  // Reset visible limit when filter changes
  useEffect(() => {
    setVisibleLimit(6);
  }, [selectedFilter]);
  const [jobs, setJobs] = useState<JobListingItem[]>([]);
  const [municipalServices, setMunicipalServices] = useState<MunicipalServiceItem[]>([]);

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const [newsRows, announcementRows, projectRows, jobRows, serviceRows] = await Promise.all([
        loadDataState(() => newsService.getAll(30), [] as NewsItem[]),
        loadDataState(() => municipalityService.getAnnouncements(60), [] as AnnouncementItem[]),
        loadDataState(() => projectService.getAll(40), [] as ProjectItem[]),
        loadDataState(() => municipalityService.getJobs(30), [] as JobListingItem[]),
        loadDataState(() => cityService.getMunicipalServices(120), [] as MunicipalServiceItem[]),
      ]);
      setNews(newsRows.data || []);
      setAnnouncements(announcementRows.data || []);
      setProjects(projectRows.data || []);
      setJobs(jobRows.data || []);
      setMunicipalServices(serviceRows.data || []);
      setSourceStates({
        news: newsRows,
        announcements: announcementRows,
        projects: projectRows,
        jobs: jobRows,
        services: serviceRows,
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = setInterval(() => void load(true), AUTO_REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  const tenders = useMemo(() => announcements.filter(isTender), [announcements]);
  const notices = useMemo(() => announcements.filter((item) => !isTender(item)), [announcements]);
  const feed = useMemo(() => buildFeed(news, announcements, projects, jobs), [news, announcements, projects, jobs]);
  const filteredFeed = useMemo(() => filterFeed(feed, selectedFilter), [feed, selectedFilter]);
  const featured = filteredFeed[0] || feed[0] || null;
  const activeProjects = projects.filter((item) => normalizeText(item.status).includes("devam")).length;
  const serviceCards = useMemo(
    () => (municipalServices.length > 0 ? municipalServices.map(serviceCardFromDb) : SERVICES),
    [municipalServices]
  );
  const sourceSummary = useMemo(
    () => summarizeSources(sourceStates ? Object.values(sourceStates) : []),
    [sourceStates]
  );

  const openFeedItem = (item: FeedItem) => {
    if (item.news) {
      navigation.navigate("NewsDetail", { news: item.news });
      return;
    }
    if (item.sourceUrl) {
      void openExternalUrl(item.sourceUrl);
    }
  };

  const openService = (service: MunicipalService) => {
    navigation.navigate("Chat", {
      presetPrompt: service.prompt,
      presetPromptId: `${service.id}-${Date.now()}`,
    });
  };

  return (
    <View style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={["top"]}>
        <AppHeader />

        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="large" color={colors.primary} />
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
            refreshControl={
              <RefreshControl
                refreshing={refreshing}
                onRefresh={() => void load(true)}
                tintColor={colors.primary}
                colors={[colors.primary]}
              />
            }
          >
            <View style={styles.introRow}>
              <View style={styles.introCopy}>
                <Text style={styles.pageTitle}>Belediye</Text>
                <Text style={styles.pageSubtitle}>Resmi akış, hizmetler ve duyurular.</Text>
              </View>
              <View style={styles.officialPill}>
                <Ionicons name="shield-checkmark-outline" size={14} color={colors.primary} />
                <Text style={styles.officialPillText}>Resmi</Text>
              </View>
            </View>

            <OfficialHero
              featured={featured}
              newsCount={news.length}
              noticeCount={notices.length}
              tenderCount={tenders.length}
              projectCount={activeProjects || projects.length}
              onPress={() => featured && openFeedItem(featured)}
            />

            {sourceSummary.error > 0 ? (
              <View style={styles.dataPanelWrap}>
                <DataStatePanel
                  tone="warning"
                  title="Resmi akış kısmen yenilendi"
                  text={`${sourceSummary.ready} kaynak cevap verdi. Cevap vermeyen kaynaklar için eski/boş bilgi kullanıcıya ayrı gösterilir.`}
                />
              </View>
            ) : sourceSummary.empty > 0 ? (
              <View style={styles.dataPanelWrap}>
                <DataStatePanel
                  title="Bazı resmi kategoriler boş"
                  text="Haber, duyuru, ihale, proje ve hizmet kaynakları ayrı kontrol edilir; kayıt gelince ekran otomatik zenginleşir."
                />
              </View>
            ) : null}

            <View style={styles.metricGrid}>
              <MetricCard label="Haber" value={news.length} icon="newspaper-outline" tone={colors.info} />
              <MetricCard label="Duyuru" value={notices.length} icon="megaphone-outline" tone={colors.primary} />
              <MetricCard label="İhale" value={tenders.length} icon="document-text-outline" tone={colors.warning} />
              <MetricCard label="Proje" value={activeProjects || projects.length} icon="construct-outline" tone={colors.tertiary} />
            </View>

            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterRow}>
              {FILTERS.map((filter) => {
                const active = selectedFilter === filter.key;
                return (
                  <TouchableOpacity
                    key={filter.key}
                    style={[styles.filterChip, active && styles.filterChipActive]}
                    onPress={() => setSelectedFilter(filter.key)}
                  >
                    <Ionicons name={filter.icon} size={14} color={active ? colors.primary : colors.textSecondary} />
                    <Text style={[styles.filterText, active && styles.filterTextActive]}>{filter.label}</Text>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>

            {selectedFilter === "services" ? (
              <Section title="BELEDİYE HİZMETLERİ" action="AI yönlendirir">
                <View style={styles.serviceGrid}>
                  {serviceCards.map((service) => (
                    <TouchableOpacity
                      key={service.id}
                      style={styles.serviceCard}
                      activeOpacity={0.88}
                      onPress={() => openService(service)}
                    >
                      <View style={styles.serviceIcon}>
                        <Ionicons name={service.icon} size={18} color={colors.primary} />
                      </View>
                      <Text style={styles.serviceTitle} numberOfLines={1}>{service.title}</Text>
                      <Text style={styles.serviceText} numberOfLines={2}>{service.description}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </Section>
            ) : (
              <Section
                title={selectedFilter === "all" ? "RESMİ AKIŞ" : selectedFilterLabel(selectedFilter).toLocaleUpperCase("tr-TR")}
                action={`${filteredFeed.length} kayıt`}
              >
                {filteredFeed.length === 0 ? (
                  <EmptyPanel title="Kayıt görünmüyor" text="Bu kategoriye ait resmi kayıt geldiğinde burada listelenecek." />
                ) : (
                  <View style={styles.feedList}>
                    {filteredFeed.slice(0, visibleLimit).map((item) => (
                      <FeedCard key={item.id} item={item} onPress={() => openFeedItem(item)} />
                    ))}
                    {filteredFeed.length > visibleLimit && (
                      <TouchableOpacity
                        style={styles.showMoreButton}
                        activeOpacity={0.8}
                        onPress={() => setVisibleLimit((prev) => prev + 10)}
                      >
                        <Text style={styles.showMoreText}>
                          Daha Fazla Göster (+{filteredFeed.length - visibleLimit})
                        </Text>
                        <Ionicons name="chevron-down-outline" size={16} color={colors.primary} />
                      </TouchableOpacity>
                    )}
                  </View>
                )}
              </Section>
            )}

            {selectedFilter !== "services" ? (
              <>
                <Section title="KURUMSAL" action="Belediyemizi Tanıyın">
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickServiceRow}>
                    <TouchableOpacity
                      style={styles.quickServiceCard}
                      activeOpacity={0.88}
                      onPress={() => navigation.navigate("Chat", {
                        presetPrompt: "Aliağa Belediye Başkanı Serkan Acar kimdir, özgeçmişi ve vizyonu hakkında bilgi ver.",
                        presetPromptId: `mayor-${Date.now()}`
                      })}
                    >
                      <Ionicons name="person-outline" size={18} color={colors.primary} />
                      <Text style={styles.quickServiceTitle} numberOfLines={2}>Başkanımız</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.quickServiceCard}
                      activeOpacity={0.88}
                      onPress={() => navigation.navigate("Chat", {
                        presetPrompt: "Aliağa Belediyesi kurumsal yapısı, meclis üyeleri, başkan yardımcıları ve vizyon/misyon hakkında bilgi ver.",
                        presetPromptId: `corporate-${Date.now()}`
                      })}
                    >
                      <Ionicons name="business-outline" size={18} color={colors.primary} />
                      <Text style={styles.quickServiceTitle} numberOfLines={2}>Kurumsal Yapı</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.quickServiceCard}
                      activeOpacity={0.88}
                      onPress={() => navigation.navigate("GalleryList")}
                    >
                      <Ionicons name="images-outline" size={18} color={colors.primary} />
                      <Text style={styles.quickServiceTitle} numberOfLines={2}>Fotoğraf Galerisi</Text>
                    </TouchableOpacity>
                  </ScrollView>
                </Section>

                <Section title="HIZLI HİZMETLER" action="Sorarak ilerle">
                <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.quickServiceRow}>
                  {serviceCards.slice(0, 4).map((service) => (
                    <TouchableOpacity
                      key={service.id}
                      style={styles.quickServiceCard}
                      activeOpacity={0.88}
                      onPress={() => openService(service)}
                    >
                      <Ionicons name={service.icon} size={18} color={colors.primary} />
                      <Text style={styles.quickServiceTitle} numberOfLines={2}>{service.title}</Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
                </Section>
              </>
            ) : null}
          </ScrollView>
        )}

      </SafeAreaView>
    </View>
  );
}

function selectedFilterLabel(filter: OfficialFilter): string {
  return FILTERS.find((item) => item.key === filter)?.label || "Resmi Akış";
}

function OfficialHero({
  featured,
  newsCount,
  noticeCount,
  tenderCount,
  projectCount,
  onPress,
}: {
  featured: FeedItem | null;
  newsCount: number;
  noticeCount: number;
  tenderCount: number;
  projectCount: number;
  onPress: () => void;
}) {
  const canOpen = Boolean(featured?.news || featured?.sourceUrl);

  return (
    <TouchableOpacity
      accessibilityRole={canOpen ? "button" : undefined}
      activeOpacity={canOpen ? 0.9 : 1}
      disabled={!canOpen}
      style={styles.featureCard}
      onPress={canOpen ? onPress : undefined}
    >
      <LinearGradient
        colors={["rgba(31,31,35,0.98)", "rgba(15,15,17,0.98)", "rgba(8,8,9,0.96)"]}
        locations={[0, 0.58, 1]}
        style={styles.featureGradient}
      >
        <View style={styles.featureGlow} />
        <View style={styles.featureTop}>
          <View style={styles.featureBadge}>
            <Ionicons name={featured?.icon || "business-outline"} size={14} color={colors.primary} />
            <Text style={styles.featureBadgeText}>{featured?.label || "Resmi Akış"}</Text>
          </View>
          <Text style={styles.featureDate}>{formatDate(featured?.date)}</Text>
        </View>

        <Text style={styles.featureKicker}>ALİAĞA BELEDİYESİ</Text>
        <Text style={styles.featureTitle} numberOfLines={2}>
          {featured?.title || "Resmi içerik bekleniyor"}
        </Text>
        <Text style={styles.featureText} numberOfLines={2}>
          {featured?.description || "Haber, duyuru, ihale ve proje kayıtları yenilendiğinde bu alan otomatik dolacak."}
        </Text>

        <View style={styles.featureFooter}>
          <HeroMiniStat value={newsCount} label="Haber" />
          <HeroMiniStat value={noticeCount} label="Duyuru" />
          <HeroMiniStat value={tenderCount} label="İhale" />
          <HeroMiniStat value={projectCount} label="Proje" />
          <View style={[styles.featureAction, !canOpen && styles.featureActionMuted]}>
            <Ionicons name={canOpen ? "arrow-forward" : "checkmark"} size={16} color={canOpen ? colors.textInverse : colors.primary} />
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
}

function HeroMiniStat({ value, label }: { value: number; label: string }) {
  return (
    <View style={styles.heroMiniStat}>
      <Text style={styles.heroMiniValue}>{value}</Text>
      <Text style={styles.heroMiniLabel}>{label}</Text>
    </View>
  );
}

function MetricCard({ label, value, icon, tone }: { label: string; value: number; icon: IconName; tone: string }) {
  return (
    <View style={styles.metricCard}>
      <View style={[styles.metricIcon, { backgroundColor: `${tone}22` }]}>
        <Ionicons name={icon} size={15} color={tone} />
        <View style={styles.metricLiveDot} />
      </View>
      <Text style={styles.metricValue}>{value}</Text>
      <Text style={styles.metricLabel} numberOfLines={1}>{label}</Text>
    </View>
  );
}

function Section({
  title,
  action,
  children,
}: {
  title: string;
  action?: string;
  children: React.ReactNode;
}) {
  return (
    <View style={styles.section}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>{title}</Text>
        {action ? <Text style={styles.sectionAction}>{action}</Text> : null}
      </View>
      {children}
    </View>
  );
}

function FeedCard({
  item,
  onPress,
}: {
  item: FeedItem;
  onPress: () => void;
}) {
  const canOpen = Boolean(item.news || item.sourceUrl);
  return (
    <TouchableOpacity style={styles.feedCard} activeOpacity={canOpen ? 0.88 : 1} onPress={canOpen ? onPress : undefined}>
      <View style={[styles.feedIcon, { backgroundColor: `${item.accent}24` }]}>
        <Ionicons name={item.icon} size={18} color={item.accent} />
      </View>
      <View style={styles.feedBody}>
        <View style={styles.feedMetaRow}>
          <Text style={styles.feedLabel}>{item.label}</Text>
          <Text style={styles.feedDate}>{formatDate(item.date)}</Text>
        </View>
        <Text style={styles.feedTitle} numberOfLines={2}>{item.title}</Text>
        {item.description ? <Text style={styles.feedText} numberOfLines={2}>{item.description}</Text> : null}
      </View>
      {canOpen ? <Ionicons name="chevron-forward" size={17} color={colors.textTertiary} /> : null}
    </TouchableOpacity>
  );
}

function EmptyPanel({ title, text }: { title: string; text: string }) {
  return (
    <View style={styles.emptyPanel}>
      <Ionicons name="file-tray-outline" size={22} color={colors.textTertiary} />
      <View style={styles.emptyBody}>
        <Text style={styles.emptyTitle}>{title}</Text>
        <Text style={styles.emptyText}>{text}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  safeArea: { flex: 1 },
  loadingWrap: { flex: 1, justifyContent: "center", alignItems: "center" },
  scrollContent: {
    paddingHorizontal: spacing.lg,
    paddingBottom: 140,
  },
  introRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: spacing.md,
    marginTop: spacing.lg,
    marginBottom: spacing.md,
  },
  introCopy: {
    flex: 1,
  },
  pageTitle: {
    fontSize: 38,
    lineHeight: 44,
    fontWeight: "800",
    color: colors.text,
    letterSpacing: 0,
  },
  pageSubtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  officialPill: {
    minHeight: 32,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.22)",
    backgroundColor: "rgba(200,169,110,0.08)",
    paddingHorizontal: spacing.sm,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  officialPillText: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  featureCard: {
    borderRadius: borderRadius.xl,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.24)",
    backgroundColor: "rgba(20,20,24,0.96)",
    marginBottom: spacing.md,
  },
  featureGradient: {
    minHeight: 238,
    padding: spacing.lg,
    justifyContent: "space-between",
  },
  featureGlow: {
    position: "absolute",
    top: -86,
    right: -64,
    width: 184,
    height: 184,
    borderRadius: 92,
    backgroundColor: "rgba(200,169,110,0.16)",
  },
  featureTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  featureBadge: {
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.24)",
    backgroundColor: "rgba(200,169,110,0.1)",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  featureBadgeText: { ...typography.captionSmall, color: colors.primary },
  featureDate: { ...typography.captionSmall, color: colors.textSecondary, textTransform: "none" },
  featureKicker: {
    ...typography.captionSmall,
    color: colors.primary,
    letterSpacing: 1.6,
    marginBottom: spacing.xs,
  },
  featureTitle: {
    fontSize: 22,
    lineHeight: 29,
    fontWeight: "800",
    color: colors.text,
    marginBottom: spacing.sm,
    letterSpacing: 0,
  },
  featureText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  featureFooter: {
    minHeight: 58,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.1)",
    backgroundColor: "rgba(10,10,10,0.52)",
    paddingHorizontal: spacing.sm,
    marginTop: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  heroMiniStat: {
    flex: 1,
  },
  heroMiniValue: {
    ...typography.caption,
    color: colors.text,
    lineHeight: 14,
  },
  heroMiniLabel: {
    ...typography.captionSmall,
    color: colors.textSecondary,
    textTransform: "none",
  },
  featureAction: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primary,
    alignItems: "center",
    justifyContent: "center",
  },
  featureActionMuted: {
    backgroundColor: "rgba(200,169,110,0.12)",
    borderWidth: 1,
    borderColor: "rgba(200,169,110,0.22)",
  },
  metricGrid: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  dataPanelWrap: {
    marginBottom: spacing.md,
  },
  metricCard: {
    flex: 1,
    minHeight: 82,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.075)",
    backgroundColor: "rgba(26,26,30,0.86)",
    padding: spacing.sm,
    justifyContent: "center",
  },
  metricIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    position: "relative",
  },
  metricLiveDot: {
    position: "absolute",
    top: 0,
    right: 0,
    width: 5,
    height: 5,
    borderRadius: 2.5,
    backgroundColor: colors.success,
  },
  metricValue: {
    fontFamily: "Outfit_800ExtraBold",
    fontSize: 18,
    lineHeight: 24,
    color: colors.primary,
    marginTop: spacing.xs,
  },
  metricLabel: { ...typography.captionSmall, color: colors.textSecondary },
  filterRow: {
    gap: spacing.sm,
    paddingBottom: spacing.xl,
  },
  filterChip: {
    height: 40,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.08)",
    backgroundColor: "rgba(30,30,34,0.82)",
    paddingHorizontal: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  filterChipActive: {
    borderColor: "rgba(200,169,110,0.72)",
    backgroundColor: "rgba(200,169,110,0.12)",
  },
  filterText: { ...typography.bodySmall, color: colors.textSecondary, fontWeight: "600" },
  filterTextActive: { color: colors.primary },
  section: {
    marginBottom: spacing.xxl,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "rgba(200,169,110,0.12)",
    paddingBottom: spacing.sm,
    marginBottom: spacing.md,
  },
  sectionTitle: { ...typography.caption, color: colors.primary, letterSpacing: 1.7 },
  sectionAction: { ...typography.captionSmall, color: colors.textTertiary, textTransform: "none" },
  feedList: {
    gap: spacing.md,
  },
  feedCard: {
    minHeight: 116,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.075)",
    backgroundColor: "rgba(24,24,28,0.9)",
    padding: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.md,
  },
  feedIcon: {
    width: 38,
    height: 38,
    borderRadius: 19,
    justifyContent: "center",
    alignItems: "center",
  },
  feedBody: { flex: 1 },
  feedMetaRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  feedLabel: { ...typography.captionSmall, color: colors.primary },
  feedDate: { ...typography.captionSmall, color: colors.textTertiary, textTransform: "none" },
  feedTitle: { ...typography.bodyMedium, color: colors.text, fontWeight: "800" },
  feedText: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },
  serviceGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
  },
  serviceCard: {
    width: "47.8%",
    minHeight: 142,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.075)",
    backgroundColor: "rgba(24,24,28,0.9)",
    padding: spacing.md,
  },
  serviceIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  serviceTitle: { ...typography.bodySmall, color: colors.text, fontWeight: "800" },
  serviceText: { ...typography.caption, color: colors.textSecondary, marginTop: spacing.xs, textTransform: "none" },
  quickServiceRow: {
    gap: spacing.md,
    paddingRight: spacing.xl,
  },
  quickServiceCard: {
    width: 126,
    minHeight: 88,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: "rgba(255,255,255,0.075)",
    backgroundColor: "rgba(24,24,28,0.9)",
    padding: spacing.md,
    justifyContent: "space-between",
  },
  quickServiceTitle: { ...typography.bodySmall, color: colors.text, fontWeight: "700" },
  emptyPanel: {
    minHeight: 98,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
    padding: spacing.lg,
    flexDirection: "row",
    alignItems: "center",
  },
  emptyBody: { flex: 1, marginLeft: spacing.md },
  emptyTitle: { ...typography.bodyMedium, color: colors.text, fontWeight: "700" },
  emptyText: { ...typography.bodySmall, color: colors.textSecondary, marginTop: 2 },
  showMoreButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(255, 255, 255, 0.03)",
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    marginTop: spacing.md,
    gap: spacing.sm,
  },
  showMoreText: {
    ...typography.bodySmall,
    color: colors.primary,
    fontWeight: "700",
  },
});
