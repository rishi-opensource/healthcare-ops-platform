import { CameraView, useCameraPermissions } from "expo-camera";
import { StyleSheet, Text, View } from "react-native";
import { Screen } from "@/components/screen";

export default function ScanTab() {
  const [permission] = useCameraPermissions();

  return (
    <Screen title="Scan" eyebrow="Barcode and QR">
      <View style={styles.cameraShell}>
        {permission?.granted ? (
          <CameraView style={styles.camera} barcodeScannerSettings={{ barcodeTypes: ["qr", "code128", "ean13"] }} />
        ) : (
          <Text style={styles.body}>Camera permission will be requested when scan workflows are activated.</Text>
        )}
      </View>
      <Text style={styles.body}>Phase 8 connects scan resolution to inventory, assets, tickets, deliveries, and forms.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  cameraShell: {
    alignItems: "center",
    aspectRatio: 1,
    backgroundColor: "#102027",
    borderRadius: 8,
    justifyContent: "center",
    overflow: "hidden"
  },
  camera: {
    height: "100%",
    width: "100%"
  },
  body: {
    color: "#5f6c7b"
  }
});

