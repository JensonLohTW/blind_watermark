import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmbedForm } from "@/components/embed-form";
import { ExtractForm } from "@/components/extract-form";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">盲浮水印系統</h1>
          <p className="text-muted-foreground mt-2">
            使用 DWT-DCT-SVD 演算法進行圖片浮水印嵌入與提取
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <Tabs defaultValue="embed" className="max-w-4xl mx-auto">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="embed">嵌入浮水印</TabsTrigger>
            <TabsTrigger value="extract">提取浮水印</TabsTrigger>
          </TabsList>

          <TabsContent value="embed" className="mt-6">
            <EmbedForm />
          </TabsContent>

          <TabsContent value="extract" className="mt-6">
            <ExtractForm />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t mt-12">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>基於 Next.js 16.0 / React 19 / FastAPI 建構</p>
        </div>
      </footer>
    </div>
  );
}
