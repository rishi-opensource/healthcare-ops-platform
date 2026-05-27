import { ReactNode } from "react";
import { SafeAreaView, StyleSheet, Text, View } from "react-native";

type ScreenProps = {
  title: string;
  eyebrow?: string;
  children: ReactNode;
};

export function Screen({ title, eyebrow, children }: ScreenProps) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        {eyebrow ? <Text style={styles.eyebrow}>{eyebrow}</Text> : null}
        <Text style={styles.title}>{title}</Text>
        <View style={styles.content}>{children}</View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#f7f8fa"
  },
  container: {
    flex: 1,
    padding: 20
  },
  eyebrow: {
    color: "#5f6c7b",
    fontSize: 12,
    fontWeight: "700",
    textTransform: "uppercase"
  },
  title: {
    color: "#17202a",
    fontSize: 26,
    fontWeight: "800",
    marginTop: 6
  },
  content: {
    marginTop: 20,
    gap: 12
  }
});

