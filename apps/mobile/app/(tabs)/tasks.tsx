import type { TicketListItem, TicketStatus } from "@healthcare/api-client";
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

export default function TasksTab() {
  const [tickets, setTickets] = useState<TicketListItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [completionSummary, setCompletionSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setMessage("");
    try {
      await hydrateToken();
      const page = await mobileApiClient().listTickets({ assigned_to: "me" });
      setTickets(page.results);
      setSelectedId((current) => current ?? page.results[0]?.id ?? null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load assigned tasks.");
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      void loadTickets();
    }, [loadTickets])
  );

  async function transition(id: number, status: TicketStatus) {
    await mobileApiClient().transitionTicket(id, status, `Updated from mobile to ${label(status)}.`);
    await loadTickets();
  }

  async function complete(id: number) {
    if (!completionSummary.trim()) return;
    await mobileApiClient().completeTicket(id, {
      completion_summary: completionSummary.trim(),
      outcome: completionSummary.trim(),
      request_approval: true
    });
    setCompletionSummary("");
    await loadTickets();
  }

  return (
    <Screen title="Assigned tasks" eyebrow="Tickets">
      {loading ? <ActivityIndicator color="#0f766e" /> : null}
      {message ? <Text style={styles.alert}>{message}</Text> : null}
      <ScrollView contentContainerStyle={styles.list}>
        {tickets.map((ticket) => {
          const active = ticket.id === selectedId;
          return (
            <Pressable
              key={ticket.id}
              onPress={() => setSelectedId(ticket.id)}
              style={[styles.card, active ? styles.cardActive : null]}
            >
              <View style={styles.row}>
                <View style={styles.titleBlock}>
                  <Text style={styles.number}>{ticket.ticket_number}</Text>
                  <Text style={styles.title}>{ticket.title}</Text>
                </View>
                <Text style={styles.pill}>{label(ticket.status)}</Text>
              </View>
              <Text style={styles.body}>{ticket.branch_name || "No branch"} · {label(ticket.priority)}</Text>
              {active ? (
                <View style={styles.actions}>
                  <Pressable style={styles.button} onPress={() => void transition(ticket.id, "in_progress")}>
                    <Text style={styles.buttonText}>Start</Text>
                  </Pressable>
                  <Pressable style={styles.buttonSecondary} onPress={() => void transition(ticket.id, "needs_correction")}>
                    <Text style={styles.buttonSecondaryText}>Correct</Text>
                  </Pressable>
                  <TextInput
                    placeholder="Completion summary"
                    placeholderTextColor="#718096"
                    style={styles.input}
                    value={completionSummary}
                    onChangeText={setCompletionSummary}
                  />
                  <Pressable style={styles.button} onPress={() => void complete(ticket.id)}>
                    <Text style={styles.buttonText}>Complete</Text>
                  </Pressable>
                </View>
              ) : null}
            </Pressable>
          );
        })}
        {!loading && tickets.length === 0 ? (
          <View style={styles.card}>
            <Text style={styles.title}>No assigned tasks</Text>
            <Text style={styles.body}>Tickets assigned to you will appear here.</Text>
          </View>
        ) : null}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: {
    gap: 12,
    paddingBottom: 28
  },
  card: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 8,
    borderWidth: 1,
    padding: 16
  },
  cardActive: {
    borderColor: "#0f766e"
  },
  row: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: 10,
    justifyContent: "space-between"
  },
  titleBlock: {
    flex: 1,
    gap: 4
  },
  number: {
    color: "#5f6c7b",
    fontSize: 12,
    fontWeight: "700"
  },
  title: {
    color: "#17202a",
    fontSize: 18,
    fontWeight: "800"
  },
  body: {
    color: "#5f6c7b",
    marginTop: 8
  },
  pill: {
    backgroundColor: "#dbeafe",
    borderRadius: 999,
    color: "#175cd3",
    fontSize: 12,
    fontWeight: "800",
    paddingHorizontal: 9,
    paddingVertical: 5
  },
  actions: {
    gap: 10,
    marginTop: 14
  },
  button: {
    alignItems: "center",
    backgroundColor: "#0f766e",
    borderRadius: 6,
    padding: 12
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "800"
  },
  buttonSecondary: {
    alignItems: "center",
    backgroundColor: "#e6f3f1",
    borderRadius: 6,
    padding: 12
  },
  buttonSecondaryText: {
    color: "#115e59",
    fontWeight: "800"
  },
  input: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 6,
    borderWidth: 1,
    color: "#17202a",
    padding: 12
  },
  alert: {
    borderColor: "#fecaca",
    borderRadius: 6,
    borderWidth: 1,
    color: "#b42318",
    padding: 10
  }
});
