chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "sendProducts") {
      const products = message.data;
      const container = document.getElementById("product-list");
      container.innerHTML = ""; // Clear existing content

      products.forEach((product) => {
          const productElement = document.createElement("div");
          productElement.className = "product";

          productElement.innerHTML = `
              <img src="${product.image}" alt="${product.title}" class="product-image" />
              <div class="product-details">
                  <h3 class="product-title">${product.title}</h3>
                  <p class="product-price">${product.price}</p>
              </div>
          `;
          container.appendChild(productElement);
      });
  }
});

// Request the content script to rescrape when the popup opens
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  chrome.tabs.sendMessage(tabs[0].id, { action: "rescrape" });
});