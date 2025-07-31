# unreal engine memo

## general


## PanoramicExporter UE5
- 出力先を変更する
  - SP.OutputDir ../../../../../Panorama
- [【UE5】 Unreal Engine 5 で360°動画 パノラマ静止画 を作成する方法！360°動画の作成 panoramic capture の導入方法を教えます チュートリアル 完全攻略](https://www.youtube.com/watch?v=zEhHdroMHbI&list=PL2_FpRIC2hFpmVl0imH3mpInUwz2D-XbM&index=1&t=330s)

## UnrealEnginePython
- [UE4でPythonを使ってみる](https://qiita.com/simonritchie/items/58fe6d4d3c411c8c062f)
- https://github.com/giwig/UnrealEnginePython
  - 4.26fork

```cs
// 
    private string[] windowsKnownPaths =
    {
       // "C:/Program Files/Python37",
        "C:/Users/{}/AppData/Local/Programs/Python/Python37",
        "C:/Program Files/Python36",
        "C:/Program Files/Python35",
        "C:/Python27",
        "C:/IntelPython35"
    };
```

```cpp
void ASceneCap::BeginPlay()
{
	Super::BeginPlay();

	if (!bCapturing) {
		// tick停止
		PrimaryActorTick.bCanEverTick = false;
		PrimaryActorTick.bStartWithTickEnabled = false;// BlueprintでActorTickカテゴリにあるフラグ
		return;
	}

	// Prepare the color data array
	ColorData.AddDefaulted(VideoSize.X * VideoSize.Y);
	ColorDataFloat.AddDefaulted(VideoSize.X * VideoSize.Y);
	int cvColorMode = GetColorMode();

	// runtime render target
	RenderTargetRuntime = NewObject<UTextureRenderTarget2D>(this);
	if (ColorMode == ETextureRenderTargetFormat::RTF_RGBA32f)
	{
		RenderTargetRuntime->InitCustomFormat(VideoSize.X, VideoSize.Y, PF_FloatRGBA, false);
	}
	else
	{
		RenderTargetRuntime->InitCustomFormat(VideoSize.X, VideoSize.Y, PF_B8G8R8A8, false);
	}
	RenderTargetRuntime->UpdateResource();

	RenderTargetOutput = NewObject<UTextureRenderTarget2D>(this);
	if (ColorMode == ETextureRenderTargetFormat::RTF_RGBA32f)
	{
		RenderTargetOutput->InitCustomFormat(VideoSize.X, VideoSize.Y, PF_FloatRGBA, false);
	}
	else
	{
		RenderTargetOutput->InitCustomFormat(VideoSize.X, VideoSize.Y, PF_B8G8R8A8, false);
	}
	RenderTargetOutput->UpdateResource();

	// scene capture
	if (!SceneCaptureCv) {
		SceneCaptureCv = NewObject<USceneCaptureComponent2D>(this);
		SceneCaptureCv->RegisterComponent();
		SceneCaptureCv->AttachToComponent(RootComponent, { EAttachmentRule::KeepRelative, false });
	}
	SceneCaptureCv->bCaptureEveryFrame = bCapturing;
	SceneCaptureCv->TextureTarget = RenderTargetRuntime;
	SceneCaptureCv->UpdateContent();
}
```
