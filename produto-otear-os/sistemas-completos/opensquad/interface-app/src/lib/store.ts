"use client";

export interface OnboardingData {
  instagramHandle: string;
  referenceProfiles: string[];
  website: string;
  niche: string;
}

const STORAGE_KEY = "otear-onboarding";

export function getOnboardingData(): OnboardingData | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveOnboardingData(data: OnboardingData) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function clearOnboardingData() {
  localStorage.removeItem(STORAGE_KEY);
}
