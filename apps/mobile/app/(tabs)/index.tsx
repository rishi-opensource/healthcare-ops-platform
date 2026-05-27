import type {
  ComplianceSummary,
  DashboardReport,
  DocumentAssignment,
  Entity,
  EntityListItem,
  EntitySummary,
  AttendanceRecord,
  TrainingAssignment,
  WorkforceSummary
} from "@healthcare/api-client";
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
  const [compliance, setCompliance] = useState<ComplianceSummary | null>(null);
  const [dashboard, setDashboard] = useState<DashboardReport | null>(null);
  const [workforce, setWorkforce] = useState<WorkforceSummary | null>(null);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [documents, setDocuments] = useState<DocumentAssignment[]>([]);
  const [training, setTraining] = useState<TrainingAssignment[]>([]);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setMessage("");
    try {
      await hydrateToken();
      const api = mobileApiClient();
      const [
        nextSummary,
        entityPage,
        complianceSummary,
        dashboardReport,
        workforceSummary,
        attendancePage,
        documentPage,
        trainingPage
      ] = await Promise.all([
        api.entitySummary(),
        api.listEntities({ status: "onboarding" }),
        api.complianceSummary(),
        api.dashboardReport(),
        api.workforceSummary(),
        api.listAttendanceRecords(),
        api.listDocumentAssignments(),
        api.listTrainingAssignments()
      ]);
      setSummary(nextSummary);
      setEntities(entityPage.results);
      setCompliance(complianceSummary);
      setDashboard(dashboardReport);
      setWorkforce(workforceSummary);
      setAttendance(attendancePage.results);
      setDocuments(documentPage.results);
      setTraining(trainingPage.results);
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

  async function acknowledgeFirstDocument() {
    const assignment = documents.find((item) => item.status === "assigned" || item.status === "viewed");
    if (!assignment) return;
    await mobileApiClient().acknowledgeDocument(
      assignment.id,
      note || "Acknowledged from mobile.",
      "Mobile acknowledgement"
    );
    setNote("");
    await load();
  }

  async function completeFirstTraining() {
    const assignment = training.find((item) => item.status === "assigned" || item.status === "in_progress" || item.status === "overdue");
    if (!assignment) return;
    await mobileApiClient().completeTraining(assignment.id, {
      completion_note: note || "Completed from mobile.",
      quiz_score: 90,
      evidence_label: "Mobile certificate"
    });
    setNote("");
    await load();
  }

  async function toggleAttendance() {
    const active = attendance.find((item) => item.status === "clocked_in");
    if (active) {
      await mobileApiClient().clockOut(active.id);
    } else {
      await mobileApiClient().clockIn({ location_label: "Mobile app" });
    }
    await load();
  }

  return (
    <Screen title="Daily operations" eyebrow="Phase 6 workspace">
      {loading ? <ActivityIndicator color="#0f766e" /> : null}
      {message ? <Text style={styles.alert}>{message}</Text> : null}
      <View style={styles.grid}>
        {[
          ["Onboarding", summary?.onboarding ?? 0],
          ["Waiting approval", summary?.waiting_approval ?? 0],
          ["Pending steps", summary?.pending_steps ?? 0],
          ["Docs pending", compliance?.pending_documents ?? 0],
          ["Training due", (compliance?.assigned_training ?? 0) - (compliance?.completed_training ?? 0)],
          ["Overdue", compliance?.overdue_training ?? 0],
          ["Due today", dashboard?.daily_workspace.due_today ?? 0],
          ["Approvals", dashboard?.tickets.pending_approvals ?? 0],
          ["Stock alerts", dashboard?.daily_workspace.stock_warnings ?? 0],
          ["Clocked in", workforce?.clocked_in ?? 0],
          ["Payroll ready", workforce?.payroll_ready ?? 0],
          ["Handovers", workforce?.open_handovers ?? 0]
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
        <View style={styles.card}>
          <Text style={styles.title}>Shift and attendance</Text>
          <View style={styles.stepRow}>
            <Text style={styles.stepName}>Upcoming shifts</Text>
            <Text style={styles.body}>{workforce?.published_shifts ?? 0}</Text>
          </View>
          <View style={styles.stepRow}>
            <Text style={styles.stepName}>Attendance exceptions</Text>
            <Text style={styles.body}>{workforce?.attendance_exceptions ?? 0}</Text>
          </View>
          <Pressable style={styles.button} onPress={() => void toggleAttendance()}>
            <Text style={styles.buttonText}>
              {attendance.some((item) => item.status === "clocked_in") ? "Clock out" : "Clock in"}
            </Text>
          </Pressable>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Manager summary</Text>
          <View style={styles.stepRow}>
            <Text style={styles.stepName}>Users working</Text>
            <Text style={styles.body}>{dashboard?.workforce.users_working ?? 0}</Text>
          </View>
          <View style={styles.stepRow}>
            <Text style={styles.stepName}>Payroll ready tasks</Text>
            <Text style={styles.body}>{dashboard?.workforce.payroll_ready ?? 0}</Text>
          </View>
          <View style={styles.stepRow}>
            <Text style={styles.stepName}>Communication follow-ups</Text>
            <Text style={styles.body}>{dashboard?.daily_workspace.communication_followups ?? 0}</Text>
          </View>
        </View>
        <View style={styles.card}>
          <Text style={styles.title}>Contracts and training</Text>
          {documents.slice(0, 3).map((assignment) => (
            <View key={`doc-${assignment.id}`} style={styles.stepRow}>
              <Text style={styles.stepName}>{assignment.template_name}</Text>
              <Text style={styles.body}>{label(assignment.status)} · {assignment.assigned_to_entity_name || assignment.assigned_to_email || "Assigned"}</Text>
            </View>
          ))}
          {training.slice(0, 3).map((assignment) => (
            <View key={`training-${assignment.id}`} style={styles.stepRow}>
              <Text style={styles.stepName}>{assignment.module_title}</Text>
              <Text style={styles.body}>{label(assignment.status)} · {assignment.certificate_label || "Certificate pending"}</Text>
            </View>
          ))}
          <TextInput
            placeholder="Acknowledgement or training note"
            placeholderTextColor="#718096"
            style={styles.input}
            value={note}
            onChangeText={setNote}
          />
          <View style={styles.buttonRow}>
            <Pressable style={[styles.button, styles.secondaryButton]} onPress={() => void acknowledgeFirstDocument()}>
              <Text style={styles.buttonText}>Acknowledge doc</Text>
            </Pressable>
            <Pressable style={styles.button} onPress={() => void completeFirstTraining()}>
              <Text style={styles.buttonText}>Complete training</Text>
            </Pressable>
          </View>
        </View>
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
  buttonRow: {
    flexDirection: "row",
    gap: 10
  },
  secondaryButton: {
    backgroundColor: "#115e59"
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
