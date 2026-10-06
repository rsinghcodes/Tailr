"use client";

import { CheckCircle2 } from "lucide-react";

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="text-xs font-bold uppercase tracking-wider mb-2.5"
      style={{ color: "var(--md-primary)" }}
    >
      {children}
    </div>
  );
}

function SkillTag({ children, dim }: { children: React.ReactNode; dim?: boolean }) {
  return (
    <span
      className="px-3 py-1 rounded-full text-xs font-medium border transition-colors inline-flex items-center"
      style={{
        background: dim ? "var(--md-surface-c1)" : "var(--md-surface-c3)",
        borderColor: dim ? "var(--md-outline)" : "var(--md-outline-v)",
        color: dim ? "var(--md-on-surface-d)" : "var(--md-on-surface-v)",
      }}
    >
      {children}
    </span>
  );
}

function SubCard({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="rounded-2xl border p-4 space-y-2 transition-all"
      style={{
        background: "var(--md-surface-c1)",
        borderColor: "var(--md-outline)",
      }}
    >
      {children}
    </div>
  );
}

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
    <div className="space-y-6">
      {summary && (
        <div className="space-y-2">
          <SectionTitle>Professional Summary</SectionTitle>
          <div
            className="text-sm leading-relaxed rounded-2xl p-4 border"
            style={{
              background: "var(--md-surface-c1)",
              borderColor: "var(--md-outline)",
              color: "var(--md-on-surface-v)",
            }}
          >
            {summary}
          </div>
        </div>
      )}

      {skills && skills.length > 0 && (
        <div>
          <SectionTitle>Skills ({skills.length})</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {skills.map((s, i) => (
              <SkillTag key={i}>
                <span style={{ color: "var(--md-on-bg)" }}>{s.name}</span>
                {s.category ? (
                  <span className="ml-1.5 opacity-60 text-[11px]">· {s.category}</span>
                ) : null}
              </SkillTag>
            ))}
          </div>
        </div>
      )}

      {experience && experience.length > 0 && (
        <div>
          <SectionTitle>Experience ({experience.length})</SectionTitle>
          <div className="space-y-3">
            {experience.map((e, i) => (
              <SubCard key={i}>
                <div className="flex items-center justify-between text-sm flex-wrap gap-1">
                  <span className="font-semibold text-base" style={{ color: "var(--md-on-bg)" }}>
                    {e.role}
                  </span>
                  <span className="font-medium text-sm" style={{ color: "var(--md-primary)" }}>
                    {e.company}
                  </span>
                </div>
                <div className="text-xs font-mono" style={{ color: "var(--md-on-surface-d)" }}>
                  {e.start_date} — {e.end_date || "Present"}
                  {e.location ? <span className="ml-2">· {e.location}</span> : null}
                  {e.employment_type ? <span className="ml-2">· {e.employment_type}</span> : null}
                </div>
                {e.technologies && e.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {e.technologies.map((t, j) => (
                      <SkillTag key={j} dim>{t}</SkillTag>
                    ))}
                  </div>
                )}
                {e.bullets && e.bullets.length > 0 && (
                  <ul className="space-y-1.5 pt-2">
                    {e.bullets.map((b, j) => (
                      <li key={j} className="text-xs sm:text-sm leading-relaxed flex items-start gap-2.5" style={{ color: "var(--md-on-surface-v)" }}>
                        <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ background: "var(--md-primary)" }} />
                        <span>{b.text}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {e.achievements && e.achievements.length > 0 && (
                  <div className="pt-2">
                    <div className="text-[11px] font-bold uppercase tracking-wider mb-1" style={{ color: "var(--md-tertiary)" }}>
                      Key Achievements
                    </div>
                    <ul className="space-y-1">
                      {e.achievements.map((a, j) => (
                        <li key={j} className="text-xs sm:text-sm flex items-start gap-2" style={{ color: "var(--md-tertiary)" }}>
                          <span className="mt-0.5">★</span>
                          <span>{a}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {education && education.length > 0 && (
        <div>
          <SectionTitle>Education</SectionTitle>
          <div className="space-y-3">
            {education.map((e, i) => (
              <SubCard key={i}>
                <div className="text-sm font-semibold" style={{ color: "var(--md-on-bg)" }}>
                  {e.degree} — <span style={{ color: "var(--md-primary)" }}>{e.institution}</span>
                  {e.field ? <span style={{ color: "var(--md-on-surface-v)" }}> ({e.field})</span> : null}
                  {e.cgpa ? <span className="ml-2 font-mono text-xs font-normal" style={{ color: "var(--md-tertiary)" }}>· CGPA: {e.cgpa}</span> : null}
                </div>
                <div className="text-xs font-mono" style={{ color: "var(--md-on-surface-d)" }}>
                  {e.start_date} — {e.end_date || "Present"}
                </div>
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div>
          <SectionTitle>Projects ({projects.length})</SectionTitle>
          <div className="space-y-3">
            {projects.map((p, i) => (
              <SubCard key={i}>
                <div className="text-sm font-semibold" style={{ color: "var(--md-on-bg)" }}>{p.title}</div>
                {p.technologies && p.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {p.technologies.map((t, j) => <SkillTag key={j} dim>{t}</SkillTag>)}
                  </div>
                )}
                {p.description && (
                  <div className="text-xs sm:text-sm leading-relaxed pt-1" style={{ color: "var(--md-on-surface-v)" }}>
                    {p.description}
                  </div>
                )}
                {p.bullets && p.bullets.length > 0 && (
                  <ul className="space-y-1.5 pt-1">
                    {p.bullets.map((b, j) => (
                      <li key={j} className="text-xs sm:text-sm leading-relaxed flex items-start gap-2.5" style={{ color: "var(--md-on-surface-v)" }}>
                        <span className="w-1.5 h-1.5 rounded-full mt-2 shrink-0" style={{ background: "var(--md-outline-v)" }} />
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {certifications && certifications.length > 0 && (
        <div>
          <SectionTitle>Certifications</SectionTitle>
          <div className="space-y-3">
            {certifications.map((c, i) => (
              <SubCard key={i}>
                <div className="text-sm font-medium" style={{ color: "var(--md-on-bg)" }}>
                  <span className="font-semibold">{c.name}</span> — {c.issuer}
                  {c.credential_id && <span className="ml-2 font-mono text-xs opacity-75">· ID: {c.credential_id}</span>}
                  {c.issue_date && <span className="ml-2 font-mono text-xs opacity-75">· {c.issue_date}</span>}
                </div>
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {achievements && achievements.length > 0 && (
        <div>
          <SectionTitle>Achievements</SectionTitle>
          <div className="space-y-3">
            {achievements.map((a, i) => (
              <SubCard key={i}>
                <div className="text-sm font-semibold" style={{ color: "var(--md-on-bg)" }}>{a.title}</div>
                {a.category && (
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full" style={{ background: "var(--md-surface-c3)", color: "var(--md-primary)" }}>
                    {a.category}
                  </span>
                )}
                {a.description && <div className="text-xs sm:text-sm mt-1" style={{ color: "var(--md-on-surface-v)" }}>{a.description}</div>}
                {a.date && <div className="text-xs font-mono mt-1" style={{ color: "var(--md-on-surface-d)" }}>{a.date}</div>}
              </SubCard>
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
  const raw = data["raw_extracted"] as Record<string, unknown> | undefined;

  const reqSkills = raw?.["required_skills"] as string[] | undefined;
  const prefSkills = raw?.["preferred_skills"] as string[] | undefined;
  const responsibilities = raw?.["responsibilities"] as string[] | undefined;
  const keywords = raw?.["keywords"] as string[] | undefined;
  const seniority = raw?.["seniority"] as string | undefined;

  return (
    <div className="space-y-5">
      <div>
        <div className="text-base font-bold" style={{ color: "var(--md-on-bg)" }}>{title}</div>
        {company && <div className="text-sm font-medium mt-0.5" style={{ color: "var(--md-primary)" }}>{company}</div>}
      </div>

      {seniority && (
        <div>
          <SectionTitle>Seniority</SectionTitle>
          <SkillTag>{seniority}</SkillTag>
        </div>
      )}

      {reqSkills && reqSkills.length > 0 && (
        <div>
          <SectionTitle>Required Skills ({reqSkills.length})</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {reqSkills.map((s, i) => <SkillTag key={i}>{s}</SkillTag>)}
          </div>
        </div>
      )}

      {prefSkills && prefSkills.length > 0 && (
        <div>
          <SectionTitle>Preferred Skills ({prefSkills.length})</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {prefSkills.map((s, i) => <SkillTag key={i}>{s}</SkillTag>)}
          </div>
        </div>
      )}

      {responsibilities && responsibilities.length > 0 && (
        <div>
          <SectionTitle>Core Responsibilities</SectionTitle>
          <ul className="space-y-2">
            {responsibilities.map((r, i) => (
              <li key={i} className="flex items-start gap-2.5 text-xs sm:text-sm leading-relaxed" style={{ color: "var(--md-on-surface-v)" }}>
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" style={{ color: "var(--md-tertiary)" }} />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {keywords && keywords.length > 0 && (
        <div>
          <SectionTitle>Keywords ({keywords.length})</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {keywords.map((k, i) => <SkillTag key={i} dim>{k}</SkillTag>)}
          </div>
        </div>
      )}
    </div>
  );
}
