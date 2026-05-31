// Frontend for the QR code generator.
// Talks to the FastAPI backend at /api/qr and renders the returned PNG.

const form = document.querySelector<HTMLFormElement>("#qr-form")!;
const input = document.querySelector<HTMLInputElement>("#data-input")!;
const image = document.querySelector<HTMLImageElement>("#qr-image")!;
const placeholder = document.querySelector<HTMLParagraphElement>("#placeholder")!;
const downloadLink = document.querySelector<HTMLAnchorElement>("#download")!;

let currentObjectUrl: string | null = null;

async function generate(data: string): Promise<void> {
  // Revoke any previous blob URL so we don't leak memory.
  if (currentObjectUrl) {
    URL.revokeObjectURL(currentObjectUrl);
    currentObjectUrl = null;
  }

  const res = await fetch(`/api/qr?data=${encodeURIComponent(data)}`);
  if (!res.ok) {
    placeholder.textContent = `Error: ${res.status} ${res.statusText}`;
    placeholder.hidden = false;
    image.hidden = true;
    downloadLink.hidden = true;
    return;
  }

  const blob = await res.blob();
  currentObjectUrl = URL.createObjectURL(blob);

  image.src = currentObjectUrl;
  image.hidden = false;
  placeholder.hidden = true;

  downloadLink.href = currentObjectUrl;
  downloadLink.hidden = false;
}

form.addEventListener("submit", (event: SubmitEvent) => {
  event.preventDefault();
  const data = input.value.trim();
  if (data.length > 0) {
    void generate(data);
  }
});
