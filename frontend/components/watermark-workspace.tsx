"use client";

import { useCallback, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { WatermarkMode } from "@/lib/types/watermark";
import { EmbedForm } from "@/components/embed-form";
import { ExtractForm } from "@/components/extract-form";

export function WatermarkWorkspace() {
  const [activeTab, setActiveTab] = useState<"embed" | "extract">("embed");
  const [lastMode, setLastMode] = useState<WatermarkMode>("str");
  const [lastLength, setLastLength] = useState<number | null>(null);
  const [lastShape, setLastShape] = useState<number[] | null>(null);

  const handleEmbedSuccess = useCallback(
    (payload: { mode: WatermarkMode; length: number | null; shape: number[] | null }) => {
      setLastMode(payload.mode);
      setLastLength(payload.length ?? null);
      setLastShape(payload.shape ?? null);
      setActiveTab("extract");
    },
    []
  );

  return (
    <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as "embed" | "extract")} className="max-w-4xl mx-auto">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="embed">嵌入浮水印</TabsTrigger>
        <TabsTrigger value="extract">提取浮水印</TabsTrigger>
      </TabsList>

      <TabsContent value="embed" className="mt-6">
        <EmbedForm onSuccess={handleEmbedSuccess} />
      </TabsContent>

      <TabsContent value="extract" className="mt-6">
        <ExtractForm
          initialMode={lastMode}
          initialLength={lastLength}
          initialShape={lastShape}
        />
      </TabsContent>
    </Tabs>
  );
}

