import { CameraView, useCameraPermissions } from "expo-camera";
import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { Screen } from "@/components/screen";
import { hydrateToken, mobileApiClient } from "@/lib/api";

export default function ScanTab() {
  const [permission] = useCameraPermissions();
  const [barcode, setBarcode] = useState("093000000001");
  const [result, setResult] = useState("");

  async function resolve(value = barcode) {
    try {
      await hydrateToken();
      const resolved = await mobileApiClient().resolveBarcode(value);
      setResult(`${resolved.target_type}: ${resolved.label}`);
    } catch (error) {
      setResult(error instanceof Error ? error.message : "Unable to resolve barcode.");
    }
  }

  return (
    <Screen title="Scan" eyebrow="Barcode and QR">
      <View style={styles.cameraShell}>
        {permission?.granted ? (
          <CameraView
            style={styles.camera}
            barcodeScannerSettings={{ barcodeTypes: ["qr", "code128", "ean13"] }}
            onBarcodeScanned={(event) => {
              setBarcode(event.data);
              void resolve(event.data);
            }}
          />
        ) : (
          <Text style={styles.body}>Camera permission will be requested when scan workflows are activated.</Text>
        )}
      </View>
      <TextInput
        placeholder="Barcode"
        placeholderTextColor="#718096"
        style={styles.input}
        value={barcode}
        onChangeText={setBarcode}
      />
      <Pressable style={styles.button} onPress={() => void resolve()}>
        <Text style={styles.buttonText}>Resolve barcode</Text>
      </Pressable>
      {result ? <Text style={styles.body}>{result}</Text> : null}
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
  },
  input: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 6,
    borderWidth: 1,
    color: "#17202a",
    marginTop: 12,
    padding: 12
  },
  button: {
    alignItems: "center",
    backgroundColor: "#0f766e",
    borderRadius: 6,
    marginTop: 10,
    padding: 12
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "800"
  }
});
