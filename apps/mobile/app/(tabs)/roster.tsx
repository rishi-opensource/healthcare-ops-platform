import { StyleSheet, Text, View } from "react-native";
import { Screen } from "@/components/screen";

export default function RosterTab() {
  return (
    <Screen title="Roster" eyebrow="Shift readiness">
      <View style={styles.card}>
        <Text style={styles.title}>Current shift</Text>
        <Text style={styles.body}>Phase 7 connects roster, leave, clock-in/out, and handover.</Text>
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

