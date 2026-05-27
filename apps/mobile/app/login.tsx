import { mobileApiClient, setStoredToken } from "@/lib/api";
import { useRouter } from "expo-router";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { Screen } from "@/components/screen";

type LoginFormValues = {
  email: string;
  password: string;
};

export default function LoginScreen() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const { control, handleSubmit, formState } = useForm<LoginFormValues>({
    defaultValues: {
      email: "admin@healthcare.local",
      password: "ChangeMe123!"
    }
  });

  async function onSubmit(values: LoginFormValues) {
    setError(null);
    try {
      const response = await mobileApiClient().login(values.email, values.password);
      await setStoredToken(response.token);
      router.replace("/(tabs)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <Screen title="Healthcare Doctors OS" eyebrow="Secure access">
      <View style={styles.form}>
        <Controller
          control={control}
          name="email"
          rules={{ required: true }}
          render={({ field }) => (
            <TextInput
              autoCapitalize="none"
              keyboardType="email-address"
              onBlur={field.onBlur}
              onChangeText={field.onChange}
              placeholder="Email"
              style={styles.input}
              value={field.value}
            />
          )}
        />
        <Controller
          control={control}
          name="password"
          rules={{ required: true }}
          render={({ field }) => (
            <TextInput
              onBlur={field.onBlur}
              onChangeText={field.onChange}
              placeholder="Password"
              secureTextEntry
              style={styles.input}
              value={field.value}
            />
          )}
        />
        {error ? <Text style={styles.error}>{error}</Text> : null}
        <Pressable style={styles.button} onPress={handleSubmit(onSubmit)} disabled={formState.isSubmitting}>
          <Text style={styles.buttonText}>{formState.isSubmitting ? "Signing in..." : "Sign in"}</Text>
        </Pressable>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  form: {
    gap: 12
  },
  input: {
    backgroundColor: "#ffffff",
    borderColor: "#d9e0e7",
    borderRadius: 8,
    borderWidth: 1,
    padding: 14
  },
  button: {
    alignItems: "center",
    backgroundColor: "#0f766e",
    borderRadius: 8,
    padding: 14
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "800"
  },
  error: {
    color: "#b42318"
  }
});

