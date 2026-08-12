"use client";

import { useMemo, useState, type ReactNode } from "react";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { HttpAgent } from "@ag-ui/client";
import { useAgUiRuntime } from "@assistant-ui/react-ag-ui";

const GLOBAL_THREAD_ID = "global-v1";

export function MyRuntimeProvider({
  children,
}: Readonly<{ children: ReactNode }>) {
  const agentUrl = process.env.NEXT_PUBLIC_AGUI_AGENT_URL;

  if (!agentUrl) {
    throw new Error(
      "NEXT_PUBLIC_AGUI_AGENT_URL is required (e.g. http://localhost:7777/agui)",
    );
  }

  const [connectionError, setConnectionError] = useState<string | null>(null);

  const agent = useMemo(
    () =>
      new HttpAgent({
        url: agentUrl,
        threadId: GLOBAL_THREAD_ID,
        headers: {
          Accept: "text/event-stream",
        },
      }),
    [agentUrl],
  );

  const runtime = useAgUiRuntime({
    agent,
    onError: (error) => {
      const message =
        error.message?.trim() ||
        "無法連線到 backend，請確認服務是否啟動且位址正確。";
      setConnectionError(message);
    },
    onCancel: () => {
      setConnectionError(null);
    },
  });

  return (
    <AssistantRuntimeProvider runtime={runtime}>
      {connectionError ? (
        <div
          role="alert"
          className="bg-destructive/10 text-destructive border-destructive/30 fixed top-0 right-0 left-0 z-50 border-b px-4 py-2 text-center text-sm"
        >
          {connectionError}
        </div>
      ) : null}
      {children}
    </AssistantRuntimeProvider>
  );
}
