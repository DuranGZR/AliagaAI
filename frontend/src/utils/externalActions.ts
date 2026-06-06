import { Linking, Platform } from "react-native";

export async function openExternalUrl(url?: string | null): Promise<boolean> {
  if (!url) return false;
  try {
    const canOpen = await Linking.canOpenURL(url);
    if (!canOpen) return false;
    await Linking.openURL(url);
    return true;
  } catch {
    return false;
  }
}

export async function openPhone(phone?: string | null): Promise<boolean> {
  if (!phone) return false;
  const sanitized = phone.replace(/[^\d+]/g, "");
  if (!sanitized) return false;
  return openExternalUrl(`tel:${sanitized}`);
}

export async function openDirections(query: string, _mapsLink?: string | null): Promise<boolean> {
  const encoded = encodeURIComponent(query);
  if (Platform.OS === "ios") {
    const appleUrl = `maps://?daddr=${encoded}`;
    try {
      await Linking.openURL(appleUrl);
      return true;
    } catch {
      // fallback
    }
  }
  return openExternalUrl(`https://www.google.com/maps/dir/?api=1&destination=${encoded}`);
}

