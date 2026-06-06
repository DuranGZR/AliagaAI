import { Platform, Alert } from "react-native";

export const showAlert = (title: string, message: string) => {
  if (Platform.OS === "web") {
    window.alert(`${title}\n\n${message}`);
  } else {
    Alert.alert(title, message);
  }
};

export const showConfirm = (
  title: string,
  message: string,
  onConfirm: () => void,
  confirmText: string = "Tamam",
  cancelText: string = "İptal",
  onCancel?: () => void
) => {
  if (Platform.OS === "web") {
    const confirmed = window.confirm(`${title}\n\n${message}`);
    if (confirmed) {
      onConfirm();
    } else if (onCancel) {
      onCancel();
    }
  } else {
    Alert.alert(title, message, [
      { text: cancelText, style: "cancel", onPress: onCancel },
      { text: confirmText, style: "destructive", onPress: onConfirm },
    ]);
  }
};

export const showPrompt = (
  title: string,
  message: string,
  onConfirm: (text: string) => void,
  defaultValue: string = ""
) => {
  if (Platform.OS === "web") {
    const val = window.prompt(`${title}\n\n${message}`, defaultValue);
    if (val !== null) {
      onConfirm(val);
    }
  } else {
    if (Alert.prompt) {
      Alert.prompt(
        title,
        message,
        [
          { text: "İptal", style: "cancel" },
          { text: "Güncelle", onPress: (text?: string) => onConfirm(text || "") }
        ],
        "plain-text",
        defaultValue
      );
    } else {
      // Android Fallback
      Alert.alert(
        title,
        message + "\n\n(Bu özellik web ve iOS platformlarında giriş penceresini destekler. Lütfen profil bilgilerinizi düzenleme ekranından güncelleyin.)"
      );
    }
  }
};
