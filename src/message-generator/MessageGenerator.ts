/**
 * MessageGenerator — signal-driven, human-sounding outreach messages.
 *
 * Produces 3 structurally distinct messages per prospect:
 *   Message 1: Lead with the signal (or industry context if low signal)
 *   Message 2: Lead with the outcome (peer-to-peer, role-driven)
 *   Message 3: Lead with a provocation (non-obvious tension point)
 *
 * Rules enforced:
 * - 60–90 word limit per message
 * - No banned openers or buzzwords
 * - Case A (relevanceScore >= 0.4): use highest signal as core hook
 * - Case B (all scores < 0.4 or empty): role + industry only, intentConfidence = 0.3
 */

import { IMessageGenerator } from '../interfaces';
import {
  MessageStrategy,
  IntentHypothesis,
  ProspectData,
  IntentSignal,
  StrategyType,
  CallToActionLevel,
} from '../types';

// ─── Constants ───────────────────────────────────────────────────────────────

const WORD_MIN = 60;
const WORD_MAX = 90;

const BANNED_OPENERS = [
  'i came across',
  'i wanted to reach out',
  'hope this finds you',
  'i hope this email finds you',
  'i thought you might be interested',
  "i don't want to take up too much of your time",
];

const BANNED_PHRASES = [
  'quick chat',
  'would love to connect',
  'this might be relevant',
  'synergies',
  'synergy',
  'leverage',
  'paradigm',
  'disruptive',
  'cutting-edge',
  'revolutionary',
  'game-changer',
  'best-in-class',
  'world-class',
  'industry-leading',
  'next-generation',
  'state-of-the-art',
  'seamless',
  'robust',
  'scalable',
  'mission-critical',
  'value-add',
  'circle back',
  'touch base',
  'move the needle',
  'think outside the box',
  'pick your brain',
];

// ─── Signal naturalisation ────────────────────────────────────────────────────

/**
 * Converts a raw signal description into a natural, human-sounding reference.
 * e.g. "funding_event detected" → "the recent funding round"
 */
function naturaliseSignal(signal: IntentSignal): string {
  const desc = signal.description.toLowerCase();
  const type = signal.type.toLowerCase();

  if (type.includes('funding') || desc.includes('funding') || desc.includes('raised') || desc.includes('series')) {
    return signal.description.replace(/funding[_\s]event\s*(detected)?/i, '').trim() || 'the recent funding round';
  }
  if (type.includes('job_change') || desc.includes('joined') || desc.includes('promoted') || desc.includes('new role')) {
    return signal.description.replace(/job[_\s]change\s*(detected)?/i, '').trim() || 'the recent leadership change';
  }
  if (type.includes('company_growth') || desc.includes('hiring') || desc.includes('headcount') || desc.includes('expansion')) {
    return signal.description.replace(/company[_\s]growth\s*(detected)?/i, '').trim() || 'the hiring push';
  }
  if (type.includes('technology') || desc.includes('tech') || desc.includes('platform') || desc.includes('migration')) {
    return signal.description.replace(/technology[_\s]adoption\s*(detected)?/i, '').trim() || 'the tech stack shift';
  }
  if (type.includes('industry_trend') || desc.includes('trend') || desc.includes('market')) {
    return signal.description.replace(/industry[_\s]trend\s*(detected)?/i, '').trim() || 'the shift happening across the industry';
  }

  return signal.description.replace(/[_]+/g, ' ').replace(/\s+detected\s*$/i, '').trim();
}

// ─── Word count & enforcement ─────────────────────────────────────────────────

function countWords(text: string): number {
  return text.split(/\s+/).filter(w => w.length > 0).length;
}

function enforceWordLimit(message: string): string {
  const words = message.split(/\s+/).filter(w => w.length > 0);
  if (words.length <= WORD_MAX) return message;

  const trimmed = words.slice(0, WORD_MAX).join(' ');
  const lastEnd = Math.max(trimmed.lastIndexOf('.'), trimmed.lastIndexOf('?'), trimmed.lastIndexOf('!'));
  if (lastEnd > trimmed.length * 0.75) {
    return trimmed.substring(0, lastEnd + 1);
  }
  return trimmed;
}

function padToMinWords(message: string, context: string): string {
  if (countWords(message) >= WORD_MIN) return message;
  return message + ` ${context}`;
}

// ─── Validation helpers ───────────────────────────────────────────────────────

function hasBannedOpener(message: string): boolean {
  const lower = message.toLowerCase();
  return BANNED_OPENERS.some(o => lower.startsWith(o));
}

function containsBannedPhrase(message: string): boolean {
  const lower = message.toLowerCase();
  return BANNED_PHRASES.some(p => lower.includes(p));
}

// ─── CTA helpers ──────────────────────────────────────────────────────────────

/**
 * Message 1 CTA — signal-specific question tied to what the signal implies.
 * Asks about capacity, team-building, or next steps relevant to the trigger.
 */
function ctaSignal(isHighSignal: boolean, signalRef: string | null, role: string): string {
  if (isHighSignal && signalRef) {
    const ref = signalRef.toLowerCase();
    if (ref.includes('fund') || ref.includes('series') || ref.includes('raised')) {
      return `Is scaling the team to match this growth already on your roadmap?`;
    }
    if (ref.includes('hire') || ref.includes('headcount') || ref.includes('expansion')) {
      return `Are you building the infrastructure to support that headcount increase?`;
    }
    if (ref.includes('join') || ref.includes('promot') || ref.includes('new role') || ref.includes('leadership')) {
      return `What does the first 90 days look like for you in this role?`;
    }
    if (ref.includes('tech') || ref.includes('platform') || ref.includes('migration')) {
      return `Is the team fully ramped on the new stack, or still mid-transition?`;
    }
    return `Is expanding capacity part of the plan for this year?`;
  }
  // Case B — no strong signal
  return `Is this a challenge you're actively working through right now?`;
}

/**
 * Message 2 CTA — references what they're trying to achieve (outcome-led).
 * Peer-to-peer tone, low friction.
 */
function ctaOutcome(role: string): string {
  const isLeader = /head|vp|chief|director|president/i.test(role);
  if (isLeader) {
    return `Worth 20 minutes to see if this maps to your roadmap?`;
  }
  return `Happy to share a concrete example if it's useful — open to it?`;
}

/**
 * Message 3 CTA — genuine challenge or open question (provocation-led).
 * Must feel different from CTAs 1 and 2.
 */
function ctaProvocation(): string {
  return `Curious what your current approach looks like — open to comparing notes?`;
}

// ─── Main class ───────────────────────────────────────────────────────────────

export class MessageGenerator implements IMessageGenerator {

  /**
   * IMessageGenerator contract entry point.
   * Accepts optional signals via the last argument for Case A/B detection.
   * When called from the legacy workflow (no signals), falls back to Case B.
   */
  generateMessage(
    strategy: MessageStrategy,
    _hypothesis: IntentHypothesis,
    prospectData: ProspectData,
    signals: IntentSignal[] = []
  ): string {
    const [msg1] = this.generateThreeMessages(strategy, _hypothesis, prospectData, signals);
    return msg1;
  }

  /**
   * Core method — generates all 3 structurally distinct messages.
   *
   * Case A (any signal relevanceScore >= 0.4): highest signal drives Message 1 & 3.
   * Case B (empty or all scores < 0.4): role + industry only.
   */
  generateThreeMessages(
    strategy: MessageStrategy,
    _hypothesis: IntentHypothesis,
    prospectData: ProspectData,
    signals: IntentSignal[]
  ): [string, string, string] {
    const firstName = prospectData.contactDetails.name.split(' ')[0];
    const { name: company, industry } = prospectData.companyContext;
    const role = prospectData.role;

    // Case A / B detection
    const strongSignals = signals.filter(s => s.relevanceScore >= 0.4);
    const isHighSignal = strongSignals.length > 0;
    const topSignal = isHighSignal
      ? strongSignals.sort((a, b) => b.relevanceScore - a.relevanceScore)[0]
      : null;
    const signalRef = topSignal ? naturaliseSignal(topSignal) : null;

    const msg1 = this.buildMessage1(firstName, company, industry, role, isHighSignal, signalRef);
    const msg2 = this.buildMessage2(firstName, company, industry, role, strategy);
    const msg3 = this.buildMessage3(firstName, company, industry, role, isHighSignal, signalRef);

    return [msg1, msg2, msg3];
  }

  // ── Message 1: Lead with the signal ──────────────────────────────────────

  private buildMessage1(
    firstName: string,
    company: string,
    industry: string,
    role: string,
    isHighSignal: boolean,
    signalRef: string | null
  ): string {
    const opening = isHighSignal && signalRef
      ? `Saw ${signalRef} at ${company} — that kind of move usually puts ${role} teams under real pressure to deliver faster.`
      : `${industry} companies at ${company}'s stage are rethinking how their ${role} function operates — the pressure to do more with less is real right now.`;

    const isLeader = /head|vp|chief|director|president/i.test(role);
    const body = `We work with ${isLeader ? 'leadership teams' : 'teams'} in ${industry} on exactly that — cutting the time between signal and action without adding headcount.`;

    const raw = `${firstName}, ${opening} ${body} ${ctaSignal(isHighSignal, signalRef, role)}`;
    return this.finalise(raw, `We've seen this pattern across ${industry} and would be glad to share what's working.`);
  }

  // ── Message 2: Lead with the outcome (no signal in line 1) ───────────────

  private buildMessage2(
    firstName: string,
    company: string,
    industry: string,
    role: string,
    strategy: MessageStrategy
  ): string {
    const outcomeMap: Record<StrategyType, string> = {
      [StrategyType.DIRECT_VALUE_ALIGNMENT]:
        `Most ${role}s I talk to in ${industry} are trying to close the gap between what the data says and what the team actually acts on.`,
      [StrategyType.INSIGHT_LED_OBSERVATION]:
        `The ${role} role in ${industry} has shifted — you're expected to own outcomes that used to sit across three different functions.`,
      [StrategyType.SOFT_CURIOSITY]:
        `Running a ${role} function at a company like ${company} means you're probably solving problems that don't have clean playbooks yet.`,
    };

    const opening = outcomeMap[strategy.type] ?? outcomeMap[StrategyType.SOFT_CURIOSITY];
    const body = `We help ${industry} teams build the infrastructure to move faster on that — without the usual six-month implementation drag.`;

    const raw = `${firstName}, ${opening} ${body} ${ctaOutcome(role)}`;
    return this.finalise(raw, `Happy to share a concrete example if it's useful.`);
  }

  // ── Message 3: Lead with a provocation ───────────────────────────────────

  private buildMessage3(
    firstName: string,
    company: string,
    industry: string,
    role: string,
    isHighSignal: boolean,
    signalRef: string | null
  ): string {
    const opening = isHighSignal && signalRef
      ? `${company}'s ${signalRef} looks like an opportunity from the outside — but from where you sit as ${role}, it probably just means more to coordinate with less margin for error.`
      : `The ${industry} companies that struggle most aren't the ones with bad strategy — they're the ones where the ${role} function is still running on processes built for a smaller version of the company.`;

    const body = `That gap between current process and current scale is exactly where we spend our time.`;

    const raw = `${firstName}, ${opening} ${body} ${ctaProvocation()}`;
    return this.finalise(raw, `Happy to share what we've seen work if you want a second opinion.`);
  }

  // ── Finalise: enforce limits, strip banned phrases, pad ──────────────────

  private finalise(message: string, padSentence: string): string {
    let msg = enforceWordLimit(message);
    msg = padToMinWords(msg, padSentence);
    msg = enforceWordLimit(msg);

    BANNED_PHRASES.forEach(phrase => {
      const escaped = phrase.replace(/[.*+?^${}()|[\]\\]/g, (char) => '\\' + char);
      msg = msg.replace(new RegExp(escaped, 'gi'), '');
    });

    return msg.replace(/\s{2,}/g, ' ').trim();
  }

  // ── Public helpers (tests & authenticity filter) ──────────────────────────

  public countWords(message: string): number {
    return countWords(message);
  }

  public containsBuzzwords(message: string): boolean {
    return containsBannedPhrase(message);
  }

  public containsCliches(message: string): boolean {
    return hasBannedOpener(message);
  }

  public hasInappropriateCallToAction(message: string, strategy: MessageStrategy): boolean {
    if (strategy.callToActionLevel === CallToActionLevel.NONE) {
      const hardCTAs = ['schedule a call', 'book a meeting', 'set up a demo', 'hop on a call', 'jump on a call'];
      return hardCTAs.some(c => message.toLowerCase().includes(c));
    }
    return false;
  }
}
