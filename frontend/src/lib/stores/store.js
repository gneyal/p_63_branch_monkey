/**
 * Svelte stores for Branch Monkey
 * Manages reactive state across the application
 */

import { writable, derived } from 'svelte/store';

// Commit tree data
export const commitTree = writable(null);

// Experiments list
export const experiments = writable([]);

// Active experiment (derived from experiments)
export const activeExperiment = derived(
  experiments,
  $experiments => $experiments.find(exp => exp.is_active) || null
);

// UI theme (light/dark)
export const theme = writable('dark');

// Modal state
export const modal = writable({
  isOpen: false,
  title: '',
  message: '',
  onConfirm: null,
  onCancel: null,
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  showInput: false,
  inputValue: '',
  inputPlaceholder: '',
});

// Toast notifications
export const toasts = writable([]);

// Loading state
export const isLoading = writable(false);

// Current repository info
export const repoInfo = writable({
  path: '',
  exists: false,
  is_git_repo: false
});

// Working tree status (uncommitted changes)
export const workingTreeStatus = writable({
  clean: true,
  staged: 0,
  modified: 0,
  untracked: 0,
  total_changes: 0
});

/**
 * Show a toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, error, info)
 * @param {number} duration - Duration in ms (0 for no auto-dismiss)
 */
export function showToast(message, type = 'info', duration = 3000) {
  const id = Date.now() + Math.random();
  const toast = { id, message, type, duration };

  toasts.update(t => [...t, toast]);

  if (duration > 0) {
    setTimeout(() => {
      toasts.update(t => t.filter(toast => toast.id !== id));
    }, duration);
  }

  return id;
}

/**
 * Dismiss a toast notification
 * @param {number} id - Toast ID
 */
export function dismissToast(id) {
  toasts.update(t => t.filter(toast => toast.id !== id));
}

/**
 * Show a modal dialog
 * @param {Object} options - Modal options
 */
export function showModal(options) {
  modal.set({
    isOpen: true,
    title: options.title || '',
    message: options.message || '',
    onConfirm: options.onConfirm || null,
    onCancel: options.onCancel || null,
    confirmText: options.confirmText || 'Confirm',
    cancelText: options.cancelText || 'Cancel',
    showInput: options.showInput || false,
    inputValue: options.inputValue || '',
    inputPlaceholder: options.inputPlaceholder || '',
  });
}

/**
 * Hide the modal
 */
export function hideModal() {
  modal.update(m => ({ ...m, isOpen: false }));
}

// Tour guide state
export const showTourGuide = writable(false);

// No backend detected (for demo/web visitors)
export const noBackendDetected = writable(false);

// Demo mode - when true, API calls return static demo data
export const isDemoMode = writable(false);

/**
 * Start the tour guide
 */
export function startTour() {
  showTourGuide.set(true);
}

/**
 * Stop the tour guide
 */
export function stopTour() {
  showTourGuide.set(false);
}
