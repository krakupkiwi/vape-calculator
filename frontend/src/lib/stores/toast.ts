import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
	id: number;
	message: string;
	type: ToastType;
}

let _id = 0;
export const toasts = writable<Toast[]>([]);

export function showToast(message: string, type: ToastType = 'success', duration = 3500) {
	const id = ++_id;
	toasts.update((t) => [...t, { id, message, type }]);
	setTimeout(() => {
		toasts.update((t) => t.filter((x) => x.id !== id));
	}, duration);
}

export function dismissToast(id: number) {
	toasts.update((t) => t.filter((x) => x.id !== id));
}
