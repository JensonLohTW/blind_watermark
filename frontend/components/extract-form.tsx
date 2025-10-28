"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { WatermarkAPI } from "@/lib/services/watermark-api";
import type { WatermarkMode } from "@/lib/types/watermark";

type ExtractFormProps = {
  initialMode?: WatermarkMode;
  initialLength?: number | null;
  initialShape?: number[] | null;
};

export function ExtractForm({
  initialMode = "str",
  initialLength,
  initialShape,
}: ExtractFormProps) {
  const [mode, setMode] = useState<WatermarkMode>(initialMode);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [watermarkLength, setWatermarkLength] = useState(initialLength ?? 0);
  const [watermarkShape, setWatermarkShape] = useState(
    initialShape && initialShape.length ? initialShape.join("x") : ""
  );
  const [passwordImg, setPasswordImg] = useState(1);
  const [passwordWm, setPasswordWm] = useState(1);
  const [loading, setLoading] = useState(false);
  const [resultText, setResultText] = useState<string | null>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMode(initialMode);
  }, [initialMode]);

  useEffect(() => {
    if (initialLength != null) {
      setWatermarkLength(initialLength);
    }
  }, [initialLength]);

  useEffect(() => {
    if (initialShape && initialShape.length) {
      setWatermarkShape(initialShape.join("x"));
    } else if (initialShape === null) {
      setWatermarkShape("");
    }
  }, [initialShape]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResultText(null);
    setResultImage(null);

    if (!imageFile) {
      setError("請選擇圖片檔案");
      return;
    }

    if (!watermarkLength || watermarkLength <= 0) {
      setError("請輸入有效的浮水印位元長度");
      return;
    }

    let shapeArray: number[] | undefined;
    if (mode === "img") {
      if (!watermarkShape.trim()) {
        setError("圖片模式需要提供浮水印形狀，如 64x64");
        return;
      }
      const parts = watermarkShape
        .split(/[,xX]/)
        .map((part) => part.trim())
        .filter(Boolean)
        .map(Number);
      if (!parts.length || parts.some((value) => !Number.isFinite(value) || value <= 0)) {
        setError("浮水印形狀格式錯誤，請使用 64x64 或 64,64");
        return;
      }
      shapeArray = parts;
    }

    setLoading(true);

    try {
      const response = await WatermarkAPI.extract(
        imageFile,
        mode,
        passwordImg,
        passwordWm,
        watermarkLength,
        shapeArray
      );

      if (response.success) {
        if (response.watermark_text) {
          setResultText(response.watermark_text);
        }
        if (response.watermark_data) {
          setResultImage(`data:image/png;base64,${response.watermark_data}`);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "發生未知錯誤");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!resultImage) return;
    const link = document.createElement("a");
    link.href = resultImage;
    link.download = "extracted-watermark.png";
    link.click();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>提取浮水印</CardTitle>
        <CardDescription>從圖片中提取浮水印內容</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="extract-mode">浮水印模式</Label>
            <Select value={mode} onValueChange={(v) => setMode(v as WatermarkMode)}>
              <SelectTrigger id="extract-mode">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="str">文字模式</SelectItem>
                <SelectItem value="img">圖片模式</SelectItem>
                <SelectItem value="bit">位元模式</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="extract-image">含浮水印的圖片</Label>
            <Input
              id="extract-image"
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files?.[0] || null)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="extract-length">浮水印位元長度</Label>
            <Input
              id="extract-length"
              type="number"
              value={watermarkLength}
              onChange={(e) => setWatermarkLength(Number(e.target.value))}
              placeholder="嵌入時的浮水印位元長度"
              min={1}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="extract-password-img">圖片密碼</Label>
              <Input
                id="extract-password-img"
                type="number"
                value={passwordImg}
                onChange={(e) => setPasswordImg(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="extract-password-wm">浮水印密碼</Label>
              <Input
                id="extract-password-wm"
                type="number"
                value={passwordWm}
                onChange={(e) => setPasswordWm(Number(e.target.value))}
              />
            </div>
          </div>

          {loading && <Progress value={undefined} />}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {resultText && (
            <Alert>
              <AlertDescription>
                <strong>提取的文字：</strong>
                <div className="mt-2 p-2 bg-muted rounded">{resultText}</div>
              </AlertDescription>
            </Alert>
          )}

          {resultImage && (
            <div className="space-y-4">
              <Alert>
                <AlertDescription>浮水印圖片提取成功！</AlertDescription>
              </Alert>
              <div className="border rounded-lg p-4">
                <img src={resultImage} alt="提取的浮水印" className="max-w-full h-auto" />
              </div>
              <Button type="button" onClick={handleDownload} className="w-full">
                下載浮水印圖片
              </Button>
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "處理中..." : "提取浮水印"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
          {mode === "img" && (
            <div className="space-y-2">
              <Label htmlFor="extract-shape">浮水印形狀</Label>
              <Input
                id="extract-shape"
                value={watermarkShape}
                onChange={(e) => setWatermarkShape(e.target.value)}
                placeholder="例如 64x64 或 64,64"
                required
              />
            </div>
          )}
