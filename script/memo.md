// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class OpenCV : ModuleRules
{
	public OpenCV(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		string OpenCVPath = Path.Combine(ModuleDirectory, "..", "..", "ThirdParty", "opencv");

		PublicIncludePaths.AddRange(
			new string[] {
				// ... add public include paths required here ...
				Path.Combine(OpenCVPath, "include")
			}
			);
				
		
		PrivateIncludePaths.AddRange(
			new string[] {
				// ... add other private include paths required here ...
				Path.Combine(OpenCVPath, "include")
			}
			);
			
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				"CoreUObject",
				"Engine",
				"InputCore",
				"RHI",
				"RenderCore",
				"Media",
				"MediaAssets"
				// ... add other public dependencies that you statically link with here ...
			}
			);
			
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore"
				// ... add private dependencies that you statically link with here ...	
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);


		// OpenCV
		if (Target.Platform == UnrealTargetPlatform.Win64)
		{
			//Add the import library
			PublicLibraryPaths.AddRange(new string[] { Path.Combine(OpenCVPath, "x64", "vc15", "lib") });
			PublicAdditionalLibraries.Add("opencv_world460.lib");

			PublicIncludePaths.AddRange(new string[] { Path.Combine(OpenCVPath, "include") });
			PublicIncludePaths.Add(Path.Combine(OpenCVPath, "x64", "vc15", "lib"));

			//Delay - load the DLL, so we can load it from the right place first
			PublicDelayLoadDLLs.Add("opencv_world460.dll");

			// Add a Runtime Dependency so the DLLs will be packaged correctly
			RuntimeDependencies.Add(Path.Combine(OpenCVPath, "x64", "vc15", "bin", "opencv_world460.dll"));
            // RuntimeDependencies.Add(Path.Combine(OpenCVPath, "x64", "vc15", "bin", "opencv_videoio_ffmpeg460_64.dll"));
        }
	}
}




pl/opencv/src
pl/opencv/src
pl/opencv/ThirdParty/opencv
