"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { WatermarkAPI } from "@/lib/services/watermark-api";
import type { WatermarkMode } from "@/lib/types/watermark";

type EmbedFormProps = {
  onSuccess?: (payload: { mode: WatermarkMode; length: number | null; shape: number[] | null }) => void;
};

export function EmbedForm({ onSuccess }: EmbedFormProps) {
  const [mode, setMode] = useState<WatermarkMode>("str");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [watermarkImage, setWatermarkImage] = useState<File | null>(null);
  const [watermarkText, setWatermarkText] = useState("");
  const [watermarkLength, setWatermarkLength] = useState(100);
  const [passwordImg, setPasswordImg] = useState(1);
  const [passwordWm, setPasswordWm] = useState(1);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [resultWmLength, setResultWmLength] = useState<number | null>(null);
  const [resultWmShape, setResultWmShape] = useState<number[] | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setResultWmLength(null);
    setResultWmShape(null);

    if (!imageFile) {
      setError("請選擇圖片檔案");
      return;
    }

    if (mode === "str" && !watermarkText) {
      setError("文字模式需要輸入浮水印文字");
      return;
    }

    if (mode === "img" && !watermarkImage) {
      setError("圖片模式需要選擇浮水印圖片");
      return;
    }

    setLoading(true);

    try {
      const response = await WatermarkAPI.embed(
        imageFile,
        mode,
        passwordImg,
        passwordWm,
        watermarkText || undefined,
        watermarkImage || undefined,
        mode === "bit" ? watermarkLength : undefined
      );

      if (response.success) {
        if (response.image_data) {
          setResult(`data:image/png;base64,${response.image_data}`);
        }
        setResultWmLength(response.watermark_length ?? null);
        setResultWmShape(response.watermark_shape ?? null);
        if (onSuccess) {
          onSuccess({
            mode,
            length: response.watermark_length ?? null,
            shape: response.watermark_shape ?? null,
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "發生未知錯誤");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result) return;
    const link = document.createElement("a");
    link.href = result;
    link.download = "watermarked-image.png";
    link.click();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>嵌入浮水印</CardTitle>
        <CardDescription>選擇圖片並設定浮水印參數</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="mode">浮水印模式</Label>
            <Select value={mode} onValueChange={(v) => setMode(v as WatermarkMode)}>
              <SelectTrigger id="mode">
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
            <Label htmlFor="image">原始圖片</Label>
            <Input
              id="image"
              type="file"
              accept="image/*"
              onChange={(e) => setImageFile(e.target.files?.[0] || null)}
              required
            />
          </div>

          {mode === "str" && (
            <div className="space-y-2">
              <Label htmlFor="watermark-text">浮水印文字</Label>
              <Input
                id="watermark-text"
                value={watermarkText}
                onChange={(e) => setWatermarkText(e.target.value)}
                placeholder="輸入浮水印文字"
                required
              />
            </div>
          )}

          {mode === "img" && (
            <div className="space-y-2">
              <Label htmlFor="watermark-image">浮水印圖片</Label>
              <Input
                id="watermark-image"
                type="file"
                accept="image/*"
                onChange={(e) => setWatermarkImage(e.target.files?.[0] || null)}
                required
              />
            </div>
          )}

          {mode === "bit" && (
            <div className="space-y-2">
              <Label htmlFor="watermark-length">位元長度</Label>
              <Input
                id="watermark-length"
                type="number"
                value={watermarkLength}
                onChange={(e) => setWatermarkLength(Number(e.target.value))}
                min={1}
                required
              />
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="password-img">圖片密碼</Label>
              <Input
                id="password-img"
                type="number"
                value={passwordImg}
                onChange={(e) => setPasswordImg(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password-wm">浮水印密碼</Label>
              <Input
                id="password-wm"
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

          {result && (
            <div className="space-y-4">
              <Alert>
                <AlertDescription className="space-y-1">
                  <div>浮水印嵌入成功！</div>
                  <div>位元長度：{resultWmLength ?? "-"}</div>
                  <div>
                    浮水印形狀：
                    {resultWmShape ? resultWmShape.join(" × ") : "無"}
                  </div>
                </AlertDescription>
              </Alert>
              <div className="border rounded-lg p-4">
                <img src={result} alt="嵌入浮水印後的圖片" className="max-w-full h-auto" />
              </div>
              <Button type="button" onClick={handleDownload} className="w-full">
                下載圖片
              </Button>
            </div>
          )}

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "處理中..." : "嵌入浮水印"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
