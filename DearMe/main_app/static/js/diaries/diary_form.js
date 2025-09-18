document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("importModal");
  const openModalBtn = document.getElementById("openModalBtn");
  const stickersContainer = document.getElementById("memory-stickers");

  // Open modal
  openModalBtn.addEventListener("click", () => modal.showModal());

  // Attach memory stickers
  document.querySelectorAll(".attach-memory").forEach(btn => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".memory-item").cloneNode(true);
      card.querySelector(".attach-memory").remove();

      // Add remove button
      const removeBtn = document.createElement("button");
      removeBtn.textContent = "×";
      removeBtn.classList.add("remove-memory-btn");
      removeBtn.type = "button";
      removeBtn.addEventListener("click", () => card.remove());

      card.appendChild(removeBtn);
      card.classList.add("sticker");
      stickersContainer.appendChild(card);
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Photos
  const photosInput = document.querySelector('input[name="photos"]');
  const photosBtn = document.querySelector('.file-button:contains("Upload Photos")');
  const photosPreview = document.getElementById('photos-preview');

  if (photosBtn && photosInput) {
    photosBtn.addEventListener('click', () => photosInput.click());

    photosInput.addEventListener('change', function() {
      photosPreview.innerHTML = "";
      Array.from(this.files).forEach(file => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.style.maxWidth = "150px";
        img.style.maxHeight = "150px";
        img.style.margin = "5px";
        photosPreview.appendChild(img);
      });
    });
  }

  // Audio
  const audioInput = document.querySelector('input[name="audio"]');
  const audioBtn = document.querySelector('.file-button:contains("Upload Audio")');
  const audioPreview = document.getElementById('audio-preview');

  if (audioBtn && audioInput) {
    audioBtn.addEventListener('click', () => audioInput.click());

    audioInput.addEventListener('change', function() {
      audioPreview.innerHTML = "";
      Array.from(this.files).forEach(file => {
        const audio = document.createElement("audio");
        audio.controls = true;
        audio.src = URL.createObjectURL(file);
        audio.style.display = "block";
        audio.style.marginTop = "5px";
        audioPreview.appendChild(audio);
      });
    });
  }
});
