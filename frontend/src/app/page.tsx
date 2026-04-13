"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
// 1. IMPORT THE NEW DOCX GENERATOR
import { generateIEEEDocx } from "@/lib/ieeeExport";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const SECTION_ORDER = [
  "Title",
  "Authors",
  "Abstract",
  "Keywords",
  "Introduction",
  "Methodology",
  "Results",
  "Conclusion",
  "Acknowledgment",
  "References",
];

const SECTION_LABELS: Record<string, string> = {
  Title: "Title",
  Authors: "Authors",
  Abstract: "Abstract",
  Keywords: "Keywords",
  Introduction: "I. Introduction",
  Methodology: "II. Methodology",
  Results: "III. Results & Discussion",
  Conclusion: "IV. Conclusion",
  Acknowledgment: "Acknowledgment",
  References: "References",
};

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4 text-current"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
    </svg>
  );
}

function StepBadge({ n, active, done }: { n: number; active: boolean; done: boolean }) {
  return (
    <div
      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300 ${
        done
          ? "bg-emerald-500 border-emerald-500 text-white"
          : active
          ? "bg-slate-900 border-slate-900 text-white"
          : "bg-white border-slate-200 text-slate-400"
      }`}
    >
      {done ? "✓" : n}
    </div>
  );
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [template, setTemplate] = useState("IEEE");
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingDocx, setExportingDocx] = useState(false);
  const [uploadedFilename, setUploadedFilename] = useState("");
  const [paper, setPaper] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState("");

  const step = paper ? 3 : uploadedFilename ? 2 : 1;

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError("");
    setPaper(null); // Reset paper state on new upload
    setUploadedFilename(""); // Reset filename to reset UI progress

    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/upload/content`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setUploadedFilename(data.filename);
    } catch (e: any) {
      setError(e.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleGenerate() {
    if (!uploadedFilename) return;
    setGenerating(true);
    setError("");
    setPaper(null); // Clear previous paper data immediately
    
    try {
      const res = await fetch(`${API}/generate/paper`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content_filename: uploadedFilename, template }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setPaper(data.paper);
    } catch (e: any) {
      setError(e.message || "Generation failed.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleExportPdf() {
    if (!paper) return;
    setExportingPdf(true);
    setError("");
    try {
      const res = await fetch(`${API}/export/pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ paper }),
      });
      if (!res.ok) throw new Error("PDF export failed.");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${paper.Title?.substring(0, 20) || "research_paper"}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setExportingPdf(false);
    }
  }

  async function handleExportDocx() {
    if (!paper) return;
    setExportingDocx(true);
    setError("");
    try {
      await generateIEEEDocx(paper);
    } catch (e: any) {
      setError(e.message || "DOCX export failed.");
    } finally {
      setExportingDocx(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f6f5f2] py-12 px-4 font-serif">
      <div className="max-w-2xl mx-auto mb-10 text-center">
        <div className="inline-flex items-center gap-2 bg-slate-900 text-white text-xs font-mono px-3 py-1 rounded-full mb-4 tracking-widest uppercase">
          AI Research Agent
        </div>
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight mb-2">
          ResearchMate
        </h1>
        <p className="text-slate-500 text-base">
          Upload your notes or draft — get a complete, formatted research paper.
        </p>
      </div>

      <div className="max-w-2xl mx-auto space-y-5">
        <div className="flex items-center gap-3 px-2 mb-2">
          <StepBadge n={1} active={step === 1} done={step > 1} />
          <div className={`flex-1 h-px transition-colors duration-300 ${step > 1 ? "bg-emerald-400" : "bg-slate-200"}`} />
          <StepBadge n={2} active={step === 2} done={step > 2} />
          <div className={`flex-1 h-px transition-colors duration-300 ${step > 2 ? "bg-emerald-400" : "bg-slate-200"}`} />
          <StepBadge n={3} active={step === 3} done={false} />
          <span className="text-xs text-slate-400 font-sans ml-1">Done</span>
        </div>

        <Card className="p-6 bg-white border-slate-100 shadow-sm space-y-4">
          <div className="flex items-center gap-3">
            <StepBadge n={1} active={step === 1} done={step > 1} />
            <h2 className="text-base font-semibold text-slate-800">Upload Research Content</h2>
          </div>
          <div className="space-y-2">
            <Label className="text-xs text-slate-500 font-sans uppercase tracking-wide">
              File (PDF, DOCX, or TXT)
            </Label>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setUploadedFilename("");
                setPaper(null);
                setError("");
              }}
              className="block w-full text-sm text-slate-500 font-sans
                file:mr-3 file:py-1.5 file:px-4 file:rounded-md file:border-0
                file:text-sm file:font-medium file:bg-slate-100 file:text-slate-700
                hover:file:bg-slate-200 cursor-pointer"
            />
          </div>
          <Button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="gap-2"
          >
            {uploading && <Spinner />}
            {uploading ? "Uploading…" : "Upload File"}
          </Button>
          {uploadedFilename && (
            <p className="text-emerald-600 text-sm font-sans flex items-center gap-1.5">
              <span>✓</span> <span className="font-medium">{uploadedFilename}</span> uploaded
            </p>
          )}
        </Card>

        <Card
          className={`p-6 bg-white border-slate-100 shadow-sm space-y-4 transition-opacity duration-300 ${
            !uploadedFilename ? "opacity-50 pointer-events-none" : ""
          }`}
        >
          <div className="flex items-center gap-3">
            <StepBadge n={2} active={step === 2} done={step > 2} />
            <h2 className="text-base font-semibold text-slate-800">Choose Format & Generate</h2>
          </div>
          <div className="space-y-2">
            <Label className="text-xs text-slate-500 font-sans uppercase tracking-wide">
              Citation Template
            </Label>
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm font-sans bg-white text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400"
            >
              <option value="IEEE">IEEE Conference</option>
              <option value="APA">APA 7th Edition</option>
              <option value="MLA">MLA 9th Edition</option>
            </select>
          </div>
          <Button
            onClick={handleGenerate}
            disabled={!uploadedFilename || generating}
            className="w-full gap-2 h-10"
          >
            {generating && <Spinner />}
            {generating ? "Generating paper… (30–60s)" : "✦ Generate Research Paper"}
          </Button>
        </Card>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm font-sans flex items-start gap-2">
            <span className="mt-0.5">⚠</span>
            <span>{error}</span>
          </div>
        )}

        {generating && (
          <div className="space-y-3 animate-pulse">
            {[120, 60, 200, 160, 140].map((h, i) => (
              <div key={i} className="bg-slate-200 rounded-lg" style={{ height: h }} />
            ))}
          </div>
        )}

        {paper && !generating && (
          <div className="space-y-4">
            <Card className="p-4 bg-slate-900 border-slate-900 flex items-center justify-between gap-3 flex-wrap">
              <div>
                <p className="text-white font-semibold text-sm">Paper ready!</p>
                <p className="text-slate-400 text-xs font-sans mt-0.5">Download your formatted paper below</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={handleExportPdf}
                  disabled={exportingPdf}
                  className="gap-2 bg-white text-slate-900 border-white hover:bg-slate-100 text-sm"
                >
                  {exportingPdf && <Spinner />}
                  {exportingPdf ? "Exporting…" : "↓ PDF"}
                </Button>
                <Button
                  onClick={handleExportDocx}
                  disabled={exportingDocx}
                  className="gap-2 bg-blue-500 hover:bg-blue-600 text-white border-transparent text-sm"
                >
                  {exportingDocx && <Spinner />}
                  {exportingDocx ? "Exporting…" : "↓ DOCX"}
                </Button>
              </div>
            </Card>

            <div className="bg-white border border-slate-100 rounded-xl shadow-sm overflow-hidden">
              {paper.Title && (
                <div className="px-8 pt-8 pb-4 text-center border-b border-slate-100">
                  <h2 className="text-xl font-bold text-slate-900 leading-snug">{paper.Title}</h2>
                  {paper.Authors && (
                    <p className="text-sm text-slate-500 font-sans mt-2">{paper.Authors}</p>
                  )}
                </div>
              )}

              {paper.Abstract && (
                <div className="px-8 py-5 border-b border-slate-100 bg-slate-50">
                  <p className="text-xs font-sans uppercase tracking-widest text-slate-400 mb-2">Abstract</p>
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{paper.Abstract}</p>
                  {paper.Keywords && (
                    <p className="text-xs text-slate-500 font-sans mt-3">
                      <span className="font-semibold">Keywords — </span>{paper.Keywords}
                    </p>
                  )}
                </div>
              )}

              {SECTION_ORDER.filter(
                (s) => !["Title", "Authors", "Abstract", "Keywords"].includes(s) && paper[s]
              ).map((section) => (
                <div key={section} className="px-8 py-5 border-b border-slate-100 last:border-b-0">
                  <p className="text-xs font-sans uppercase tracking-widest text-blue-600 font-semibold mb-2">
                    {SECTION_LABELS[section] || section}
                  </p>
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                    {paper[section]}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}