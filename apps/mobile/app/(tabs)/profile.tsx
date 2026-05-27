import { StyleSheet, Text, View } from "react-native";
import { Screen } from "@/components/screen";

export default function ProfileTab() {
  return (
    <Screen title="Profile" eyebrow="Account">
      <View style={styles.card}>
        <Text style={styles.title}>Role-aware account shell</Text>
        <Text style={styles.body}>Phase 2 stores auth token and Phase 3+ adds own work, documents, training, and payroll status.</Text>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 8,
    borderWidth: 1,
    padding: 16
  },
  title: {
    color: "#17202a",
    fontSize: 18,
    fontWeight: "800"
  },
  body: {
    color: "#5f6c7b",
    marginTop: 6
  }
});

