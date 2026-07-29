"use client";

import { CheckCircle2 } from "lucide-react";

export function ParsedResumeView({ data }: { data: Record<string, unknown> }) {
  const summary = data["summary"] as string | undefined;
  const skills = data["skills"] as Array<{ name: string; category?: string }> | undefined;
  const experience = data["experience"] as Array<{
    company: string; role: string; location?: string; employment_type?: string;
    start_date: string; end_date?: string; technologies?: string[];
    bullets?: Array<{ text: string }>; achievements?: string[];
  }> | undefined;
  const education = data["education"] as Array<{
    institution: string; degree: string; field?: string; cgpa?: string;
    start_date: string; end_date?: string;
  }> | undefined;
  const projects = data["projects"] as Array<{
    title: string; description?: string; technologies?: string[]; bullets?: string[];
  }> | undefined;
  const certifications = data["certifications"] as Array<{
    name: string; issuer: string; credential_id?: string; issue_date?: string;
  }> | undefined;
  const achievements = data["achievements"] as Array<{
    title: string; description?: string; category?: string; date?: string;
  }> | undefined;

  return (
    <div className="space-y-4">
      {summary && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1">Professional Summary</div>
          <div className="text-xs text-zinc-300 leading-relaxed bg-zinc-900 border border-zinc-800 rounded-md p-3">{summary}</div>
        </div>
      )}

      {skills && skills.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Skills ({skills.length})</div>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700 text-[11px] font-mono">
                {s.name}{s.category ? <span className="text-zinc-500 ml-1">· {s.category}</span> : null}
              </span>
            ))}
          </div>
        </div>
      )}

      {experience && experience.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Experience ({experience.length})</div>
          <div className="space-y-2">
            {experience.map((e, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-md p-3 space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-zinc-200">{e.role}</span>
                  <span className="text-zinc-400">{e.company}</span>
                </div>
                <div className="text-[11px] text-zinc-500 font-mono">
                  {e.start_date} — {e.end_date || "Present"}
                  {e.location ? <span className="text-zinc-600 ml-2">· {e.location}</span> : null}
                  {e.employment_type ? <span className="text-zinc-600 ml-2">· {e.employment_type}</span> : null}
                </div>
                {e.technologies && e.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-0.5">
                    {e.technologies.map((t, j) => (
                      <span key={j} className="px-1.5 py-0.5 rounded bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
                {e.bullets && e.bullets.length > 0 && (
                  <ul className="space-y-0.5 pt-1">
                    {e.bullets.map((b, j) => (
                      <li key={j} className="text-[11px] text-zinc-400 flex items-start gap-1.5">
                        <span className="text-zinc-600 mt-px">·</span>
                        <span>{b.text}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {e.achievements && e.achievements.length > 0 && (
                  <div className="pt-0.5">
                    <div className="text-[10px] font-semibold text-zinc-500 uppercase font-mono mb-0.5">Achievements</div>
                    <ul className="space-y-0.5">
                      {e.achievements.map((a, j) => (
                        <li key={j} className="text-[11px] text-emerald-400/80 flex items-start gap-1.5">
                          <span className="text-emerald-600 mt-px">★</span>
                          <span>{a}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {education && education.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Education</div>
          <div className="space-y-1.5">
            {education.map((e, i) => (
              <div key={i} className="text-xs text-zinc-300 bg-zinc-900 border border-zinc-800 rounded-md p-2.5">
                <span className="font-semibold">{e.degree}</span> — {e.institution}
                {e.field ? <span className="text-zinc-400"> ({e.field})</span> : null}
                {e.cgpa ? <span className="text-zinc-500 ml-2">· CGPA: {e.cgpa}</span> : null}
                <div className="text-[11px] text-zinc-500 font-mono mt-0.5">{e.start_date} — {e.end_date || "Present"}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Projects ({projects.length})</div>
          <div className="space-y-2">
            {projects.map((p, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-md p-2.5 space-y-1">
                <div className="text-xs font-semibold text-zinc-200">{p.title}</div>
                {p.technologies && p.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {p.technologies.map((t, j) => (
                      <span key={j} className="px-1.5 py-0.5 rounded bg-zinc-800/50 text-zinc-400 border border-zinc-700/50 text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
                {p.description && <div className="text-[11px] text-zinc-400 leading-relaxed">{p.description}</div>}
                {p.bullets && p.bullets.length > 0 && (
                  <ul className="space-y-0.5 pt-0.5">
                    {p.bullets.map((b, j) => (
                      <li key={j} className="text-[11px] text-zinc-400 flex items-start gap-1.5">
                        <span className="text-zinc-600 mt-px">·</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {certifications && certifications.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Certifications</div>
          <div className="space-y-1.5">
            {certifications.map((c, i) => (
              <div key={i} className="text-xs text-zinc-300 bg-zinc-900 border border-zinc-800 rounded-md p-2.5">
                <span className="font-semibold">{c.name}</span> — {c.issuer}
                {c.credential_id && <span className="text-zinc-500 ml-2">· ID: {c.credential_id}</span>}
                {c.issue_date && <span className="text-zinc-500 ml-2">· {c.issue_date}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {achievements && achievements.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Achievements</div>
          <div className="space-y-1.5">
            {achievements.map((a, i) => (
              <div key={i} className="bg-zinc-900 border border-zinc-800 rounded-md p-2.5">
                <div className="text-xs font-semibold text-zinc-200">{a.title}</div>
                {a.category && <span className="text-[10px] text-zinc-500 font-mono uppercase">{a.category}</span>}
                {a.description && <div className="text-[11px] text-zinc-400 mt-0.5">{a.description}</div>}
                {a.date && <div className="text-[10px] text-zinc-500 font-mono mt-0.5">{a.date}</div>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function JdDetailView({ data }: { data: Record<string, unknown> }) {
  const title = data["title"] as string | undefined;
  const company = data["company"] as string | undefined;
  const reqs = data["parsed_requirements"] as Record<string, unknown> | undefined;
  const reqSkills = reqs?.["required_skills"] as string[] | undefined;
  const prefSkills = reqs?.["preferred_skills"] as string[] | undefined;
  const responsibilities = reqs?.["responsibilities"] as string[] | undefined;
  const softSkills = reqs?.["soft_skills"] as string[] | undefined;
  const keywords = reqs?.["keywords"] as string[] | undefined;

  return (
    <div className="space-y-3">
      <div>
        <div className="text-xs font-semibold text-zinc-200">{title}</div>
        {company && <div className="text-xs text-zinc-400">{company}</div>}
      </div>

      {reqSkills && reqSkills.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Required Skills ({reqSkills.length})</div>
          <div className="flex flex-wrap gap-1.5">
            {reqSkills.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-200 border border-zinc-700 text-[11px] font-mono">{s}</span>
            ))}
          </div>
        </div>
      )}

      {prefSkills && prefSkills.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Preferred Skills ({prefSkills.length})</div>
          <div className="flex flex-wrap gap-1.5">
            {prefSkills.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 text-[11px] font-mono">{s}</span>
            ))}
          </div>
        </div>
      )}

      {responsibilities && responsibilities.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Core Responsibilities</div>
          <ul className="space-y-1">
            {responsibilities.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-zinc-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-px" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {softSkills && softSkills.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Soft Skills</div>
          <div className="flex flex-wrap gap-1.5">
            {softSkills.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 text-[11px] font-mono">{s}</span>
            ))}
          </div>
        </div>
      )}

      {keywords && keywords.length > 0 && (
        <div>
          <div className="text-xs font-semibold text-zinc-500 uppercase font-mono mb-1.5">Keywords</div>
          <div className="flex flex-wrap gap-1.5">
            {keywords.map((k, i) => (
              <span key={i} className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700 text-[10px] font-mono">{k}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
