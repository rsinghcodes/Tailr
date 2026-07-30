"use client";

import { CheckCircle2 } from "lucide-react";

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <div className="section-label mb-2">{children}</div>;
}

function SkillTag({ children, dim }: { children: React.ReactNode; dim?: boolean }) {
  return (
    <span className={`px-2 py-0.5 rounded-md border text-[11px] font-mono ${
      dim ? "border-[var(--border-subtle)] text-[var(--text-muted)]" : "border-[var(--border-subtle)] text-[var(--text-secondary)]"
    }`} style={{ background: 'var(--bg-surface)' }}>
      {children}
    </span>
  );
}

function SubCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-[var(--border-subtle)] p-3 space-y-1" style={{ background: 'var(--bg-surface)' }}>
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
    <div className="space-y-5">
      {summary && (
        <div>
          <SectionTitle>Professional Summary</SectionTitle>
          <div className="text-xs text-[var(--text-secondary)] leading-relaxed">{summary}</div>
        </div>
      )}

      {skills && skills.length > 0 && (
        <div>
          <SectionTitle>Skills ({skills.length})</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((s, i) => (
              <SkillTag key={i}>{s.name}{s.category ? <span className="text-[var(--text-muted)] ml-1">· {s.category}</span> : null}</SkillTag>
            ))}
          </div>
        </div>
      )}

      {experience && experience.length > 0 && (
        <div>
          <SectionTitle>Experience ({experience.length})</SectionTitle>
          <div className="space-y-2">
            {experience.map((e, i) => (
              <SubCard key={i}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-[var(--text-primary)]">{e.role}</span>
                  <span className="text-[var(--text-muted)]">{e.company}</span>
                </div>
                <div className="text-[11px] text-[var(--text-muted)]">
                  {e.start_date} — {e.end_date || "Present"}
                  {e.location ? <span className="text-[var(--text-muted)] ml-2">· {e.location}</span> : null}
                  {e.employment_type ? <span className="text-[var(--text-muted)] ml-2">· {e.employment_type}</span> : null}
                </div>
                {e.technologies && e.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-0.5">
                    {e.technologies.map((t, j) => <SkillTag key={j} dim>{t}</SkillTag>)}
                  </div>
                )}
                {e.bullets && e.bullets.length > 0 && (
                  <ul className="space-y-0.5 pt-1">
                    {e.bullets.map((b, j) => (
                      <li key={j} className="text-[11px] text-[var(--text-muted)] flex items-start gap-1.5">
                        <span className="text-[var(--text-muted)] mt-px">·</span>
                        <span>{b.text}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {e.achievements && e.achievements.length > 0 && (
                  <div className="pt-0.5">
                    <div className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-0.5">Achievements</div>
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
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {education && education.length > 0 && (
        <div>
          <SectionTitle>Education</SectionTitle>
          <div className="space-y-1.5">
            {education.map((e, i) => (
              <SubCard key={i}>
                <div className="text-xs text-[var(--text-primary)]">
                  <span className="font-medium">{e.degree}</span> — {e.institution}
                  {e.field ? <span className="text-[var(--text-muted)]"> ({e.field})</span> : null}
                  {e.cgpa ? <span className="text-[var(--text-muted)] ml-2">· CGPA: {e.cgpa}</span> : null}
                </div>
                <div className="text-[11px] text-[var(--text-muted)]">{e.start_date} — {e.end_date || "Present"}</div>
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {projects && projects.length > 0 && (
        <div>
          <SectionTitle>Projects ({projects.length})</SectionTitle>
          <div className="space-y-2">
            {projects.map((p, i) => (
              <SubCard key={i}>
                <div className="text-xs font-medium text-[var(--text-primary)]">{p.title}</div>
                {p.technologies && p.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-0.5">
                    {p.technologies.map((t, j) => <SkillTag key={j} dim>{t}</SkillTag>)}
                  </div>
                )}
                {p.description && <div className="text-[11px] text-[var(--text-muted)] leading-relaxed pt-0.5">{p.description}</div>}
                {p.bullets && p.bullets.length > 0 && (
                  <ul className="space-y-0.5 pt-0.5">
                    {p.bullets.map((b, j) => (
                      <li key={j} className="text-[11px] text-[var(--text-muted)] flex items-start gap-1.5">
                        <span className="text-[var(--text-muted)] mt-px">·</span>
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
          <div className="space-y-1.5">
            {certifications.map((c, i) => (
              <SubCard key={i}>
                <div className="text-xs text-[var(--text-primary)]">
                  <span className="font-medium">{c.name}</span> — {c.issuer}
                  {c.credential_id && <span className="text-[var(--text-muted)] ml-2">· ID: {c.credential_id}</span>}
                  {c.issue_date && <span className="text-[var(--text-muted)] ml-2">· {c.issue_date}</span>}
                </div>
              </SubCard>
            ))}
          </div>
        </div>
      )}

      {achievements && achievements.length > 0 && (
        <div>
          <SectionTitle>Achievements</SectionTitle>
          <div className="space-y-1.5">
            {achievements.map((a, i) => (
              <SubCard key={i}>
                <div className="text-xs font-medium text-[var(--text-primary)]">{a.title}</div>
                {a.category && <span className="text-[10px] text-[var(--text-muted)] uppercase">{a.category}</span>}
                {a.description && <div className="text-[11px] text-[var(--text-muted)] mt-0.5">{a.description}</div>}
                {a.date && <div className="text-[10px] text-[var(--text-muted)] mt-0.5">{a.date}</div>}
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
    <div className="space-y-4">
      <div>
        <div className="text-sm font-medium text-[var(--text-primary)]">{title}</div>
        {company && <div className="text-xs text-[var(--text-muted)]">{company}</div>}
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
          <div className="flex flex-wrap gap-1.5">
            {reqSkills.map((s, i) => <SkillTag key={i}>{s}</SkillTag>)}
          </div>
        </div>
      )}

      {prefSkills && prefSkills.length > 0 && (
        <div>
          <SectionTitle>Preferred Skills ({prefSkills.length})</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {prefSkills.map((s, i) => <SkillTag key={i}>{s}</SkillTag>)}
          </div>
        </div>
      )}

      {responsibilities && responsibilities.length > 0 && (
        <div>
          <SectionTitle>Core Responsibilities</SectionTitle>
          <ul className="space-y-1">
            {responsibilities.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-[var(--text-secondary)]">
                <CheckCircle2 className="w-3.5 h-3.5 text-[var(--text-muted)] shrink-0 mt-px" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {keywords && keywords.length > 0 && (
        <div>
          <SectionTitle>Keywords ({keywords.length})</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {keywords.map((k, i) => <SkillTag key={i} dim>{k}</SkillTag>)}
          </div>
        </div>
      )}
    </div>
  );
}
