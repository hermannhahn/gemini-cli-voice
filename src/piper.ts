import { spawn, spawnSync } from "child_process";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";
import { BIN_DIR } from "./constants";

export async function runSpeechTask(
	piperExe: string,
	modelFile: string,
	lengthScale: number,
	text: string,
): Promise<string | null> {
	const system = os.platform();
	const tempWav = path.join(os.tmpdir(), `gemini-voice-${Date.now()}.wav`);

	try {
		const env = { ...process.env };
		let espeakData: string | undefined;

		if (system === "linux") {
			const linuxBinDir = path.join(BIN_DIR, "linux");
			env.LD_LIBRARY_PATH = `${linuxBinDir}:${env.LD_LIBRARY_PATH || ""}`;
			espeakData = path.join(linuxBinDir, "espeak-ng-data");
			// Ensure execution permission
			if (fs.existsSync(piperExe)) {
				fs.chmodSync(piperExe, 0o755);
			}
		} else if (system === "win32") {
			espeakData = path.join(BIN_DIR, "windows", "espeak-ng-data");
		}

		// 1. Piper generates the WAV
		const piperArgs = [
			"-q",
			"--model",
			modelFile,
			"--length_scale",
			lengthScale.toString(),
			"--output_file",
			tempWav,
		];

		if (espeakData && fs.existsSync(espeakData)) {
			piperArgs.push("--espeak_data", espeakData);
		}

		await new Promise<void>((resolve, reject) => {
			const piperProcess = spawn(piperExe, piperArgs, { env, stdio: ["pipe", "ignore", "inherit"] });

			piperProcess.on("error", reject);
			piperProcess.on("exit", (code) => {
				if (code === 0) resolve();
				else reject(new Error(`Piper exited with code ${code}`));
			});

			piperProcess.stdin.write(text);
			piperProcess.stdin.end();
		});

		// 2. Play WAV
		if (system === "linux") {
			// Try system aplay first
			let aplayExe: string | undefined;
			try {
				const res = spawnSync("which", ["aplay"], { encoding: "utf8" });
				if (res.status === 0) aplayExe = res.stdout.trim();
			} catch {}

			if (!aplayExe) {
				const localAplay = path.join(BIN_DIR, "linux", "aplay");
				if (fs.existsSync(localAplay)) {
					fs.chmodSync(localAplay, 0o755);
					aplayExe = localAplay;
				}
			}

			if (aplayExe) {
				spawnSync(aplayExe, [tempWav], { env, stdio: "ignore" });
			} else {
				return "Error: aplay not found.";
			}
		} else if (system === "win32") {
			const psCmd = `(New-Object Media.SoundPlayer '${tempWav}').PlaySync()`;
			spawnSync("powershell", ["-c", psCmd], { stdio: "ignore" });
		}

		return null;
	} catch (error) {
		return error instanceof Error ? error.message : String(error);
	} finally {
		if (fs.existsSync(tempWav)) {
			try {
				fs.unlinkSync(tempWav);
			} catch {}
		}
	}
}
