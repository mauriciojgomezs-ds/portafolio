"use strict";
document.querySelectorAll("[data-video-embed]").forEach(button => {
  button.addEventListener("click", () => {
    const iframe = document.createElement("iframe");
    iframe.src = button.dataset.videoEmbed;
    iframe.title = button.dataset.videoTitle;
    iframe.allow = "fullscreen; picture-in-picture";
    iframe.allowFullscreen = true;
    iframe.referrerPolicy = "strict-origin-when-cross-origin";
    button.replaceWith(iframe);
  });
});
