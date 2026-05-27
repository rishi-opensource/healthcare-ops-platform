import type { Entity, EntityListItem, EntitySummary } from "@healthcare/api-client";
import { useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { Screen } from "@/components/screen";
import { hydrateToken, mobileApiClient } from "@/lib/api";

function label(value: string) {
  return value
    .split("_")
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join(" ");
}

export default function HomeTab() {
  const [summary, setSummary] = useState<EntitySummary | null>(null);
  const [entities, setEntities] = useState<EntityListItem[]>([]);
  const [selected, setSelected] = useState<Entity | null>(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setMessage("");
    try {
      await hydrateToken();
      const api = mobileApiClient();
      const [nextSummary, entityPage] = await Promise.all([
        api.entitySummary(),
        api.listEntities({ status: "onboarding" })
      ]);
      setSummary(nextSummary);
      setEntities(entityPage.results);
      if (!selected && entityPage.results[0]) {
        setSelected(await api.getEntity(entityPage.results[0].id));
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load onboarding.");
    } finally {
      setLoading(false);
    }
  }, [selected]);

  useFocusEffect(
    useCallback(() => {
      void load();
    }, [load])
  );

  async function selectEntity(id: number) {
    setSelected(await mobileApiClient().getEntity(id));
  }

  async function completeFirstPending() {
    if (!selected?.onboarding) return;
    const step = selected.onboarding.step_completions.find((item) => item.status === "pending" || item.status === "needs_correction");
    if (!step) return;
    await mobileApiClient().completeOnboardingStep(
      selected.id,
      step.id,
      "completed",
      note || "Completed from mobile.",
      "Mobile evidence note"
    );
    setNote("");
    setSelected(await mobileApiClient().getEntity(selected.id));
    await load();
  }

  return (
    <Screen title="Daily operations" eyebrow="Phase 4 onboarding">
      {loading ? <ActivityIndicator color="#0f766e" /> : null}
      {message ? <Text style={styles.alert}>{message}</Text> : null}
      <View style={styles.grid}>
        {[
          ["Onboarding", summary?.onboarding ?? 0],
          ["Waiting approval", summary?.waiting_approval ?? 0],
          ["Pending steps", summary?.pending_steps ?? 0],
          ["Active", summary?.active ?? 0]
        ].map(([name, value]) => (
          <View key={name} style={styles.card}>
            <Text style={styles.label}>{name}</Text>
            <Text style={styles.value}>{value}</Text>
          </View>
        ))}
      </View>
      <ScrollView contentContainerStyle={styles.list}>
        {entities.map((entity) => (
          <Pressable key={entity.id} style={[styles.card, selected?.id === entity.id ? styles.cardActive : null]} onPress={() => void selectEntity(entity.id)}>
            <Text style={styles.title}>{entity.display_name}</Text>
            <Text style={styles.body}>{label(entity.entity_type)} · {entity.completed_step_count}/{entity.required_step_count} steps</Text>
          </Pressable>
        ))}
        {selected?.onboarding ? (
          <View style={styles.card}>
            <Text style={styles.title}>{selected.display_name}</Text>
            {selected.onboarding.step_completions.map((step) => (
              <View key={step.id} style={styles.stepRow}>
                <Text style={styles.stepName}>{step.name}</Text>
                <Text style={styles.body}>{label(step.status)}</Text>
              </View>
            ))}
            <TextInput
              placeholder="Completion note"
              placeholderTextColor="#718096"
              style={styles.input}
              value={note}
              onChangeText={setNote}
            />
            <Pressable style={styles.button} onPress={() => void completeFirstPending()}>
              <Text style={styles.buttonText}>Complete next step</Text>
            </Pressable>
          </View>
        ) : null}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10
  },
  list: {
    gap: 12,
    paddingBottom: 28
  },
  card: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 8,
    borderWidth: 1,
    minWidth: "47%",
    padding: 16
  },
  cardActive: {
    borderColor: "#0f766e"
  },
  label: {
    color: "#5f6c7b"
  },
  value: {
    color: "#17202a",
    fontSize: 24,
    fontWeight: "800",
    marginTop: 6
  },
  title: {
    color: "#17202a",
    fontSize: 18,
    fontWeight: "800"
  },
  body: {
    color: "#5f6c7b",
    marginTop: 6
  },
  stepRow: {
    borderBottomColor: "#eef2f5",
    borderBottomWidth: 1,
    paddingVertical: 8
  },
  stepName: {
    color: "#17202a",
    fontWeight: "700"
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
  },
  alert: {
    borderColor: "#fecaca",
    borderRadius: 6,
    borderWidth: 1,
    color: "#b42318",
    padding: 10
  }
});
