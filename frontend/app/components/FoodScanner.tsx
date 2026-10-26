"use client";

import { BrowserMultiFormatReader } from "@zxing/browser";
import { useEffect, useRef, useState } from "react";

export function FoodScanner({
  onCode,
  onError,
}: {
  onCode: (code: string) => void;
  onError: (message: string) => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (!active || !videoRef.current) return;
    const reader = new BrowserMultiFormatReader();
    let stopped = false;
    let stop = () => {};
    reader
      .decodeFromVideoDevice(undefined, videoRef.current, (result) => {
        if (stopped || !result) return;
        stopped = true;
        stop();
        setActive(false);
        onCode(result.getText());
      })
      .then((controls) => {
        stop = () => controls.stop();
        if (stopped) controls.stop();
      })
      .catch(() => {
        setActive(false);
        onError("The camera couldn't start. Allow camera access, or type the barcode.");
      });
    return () => {
      stopped = true;
      stop();
    };
  }, [active, onCode, onError]);

  async function onPhoto(file: File) {
    const url = URL.createObjectURL(file);
    try {
      const result = await new BrowserMultiFormatReader().decodeFromImageUrl(url);
      onCode(result.getText());
    } catch {
      onError("We couldn't read a barcode in that photo. Try the camera, or type the numbers under the bars.");
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <button className="btn" type="button" onClick={() => setActive(true)} disabled={active}>
          {active ? "Looking for a barcode…" : "Scan with camera"}
        </button>
        {active && (
          <button className="btn btn-secondary" type="button" onClick={() => setActive(false)}>
            Stop camera
          </button>
        )}
        <label className="btn btn-secondary cursor-pointer">
          Photo of a barcode
          <input
            className="hidden"
            type="file"
            accept="image/*"
            capture="environment"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (file) void onPhoto(file);
            }}
          />
        </label>
      </div>
      {active && <video ref={videoRef} className="w-full max-h-72 rounded-lg bg-black" muted playsInline />}
    </div>
  );
}
