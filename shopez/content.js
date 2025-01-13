function scrapeAmazonProductPage() {
  const product = {};

  // Scrape the title
  product.title = document.querySelector("#productTitle")?.innerText.trim() || "Unknown Product";

  // Scrape the price
  const priceWhole = document.querySelector(".a-price-whole")?.innerText || null;
  const priceFraction = document.querySelector(".a-price-fraction")?.innerText || null;
  product.price = priceWhole ? `${priceWhole}.${priceFraction || "00"}` : "N/A";

  // Scrape the image URL
  product.image =
      document.querySelector("#imgTagWrapperId img")?.src ||
      document.querySelector(".image-item img")?.src ||
      "No Image Available";

  console.log(product);
  return product;
}

function scrapeFlipkartProductPage() {
  const product = {};

  // Scrape the title
  product.title = document.querySelector(".VU-ZEz")?.innerText.trim() || "Unknown Product";

  // Scrape the price
  product.price = document.querySelector(".Nx9bqj")?.innerText.trim() || "N/A";

  // Scrape the image URL
  product.image =
      document.querySelector("._53J4C-")?.src ||
      "No Image Available";

  console.log(product);
  return product;
}

function scrapeMyntraProductPage() {
  const product = {};

  // Scrape the title
  title1 = document.querySelector(".pdp-title")?.innerText.trim() || "Unknown Product";
  title2 = document.querySelector(".pdp-name")?.innerText.trim() || "Unknown Product";
  product.title = `${title1} | ${title2}`;

  // Scrape the price
  product.price = document.querySelector(".pdp-price")?.innerText.trim() || "N/A";

  // Scrape the image URL
  const divElement = document.querySelector(".image-grid-image");
  const styleAttribute = divElement?.getAttribute("style");

  if (styleAttribute) {
      const urlMatch = styleAttribute.match(/url\("(.+?)"\)/);
      const imageUrl = urlMatch ? urlMatch[1] : null;
      if (imageUrl) {
          console.log(imageUrl);
          product.image = imageUrl;
      } else {
          console.log("No image URL found");
      }
  } else {
      console.log("No style attribute found");
  }

  console.log(product);
  return product;
}

function scrapeProducts() {
  const url = window.location.href;

  if (url.includes("amazon.in") && url.includes("/dp/")) {
      return [scrapeAmazonProductPage()];
  } else if (url.includes("flipkart.com") && url.includes("/p/")) {
      return [scrapeFlipkartProductPage()];
  } else if (url.includes("myntra.com") || url.includes("/p/")) {
    return [scrapeMyntraProductPage()];
  }

  return [];
}

function sendScrapedData() {
  const data = scrapeProducts();
  chrome.runtime.sendMessage({ action: "sendProducts", data });
}

// Scrape data once the page loads
window.addEventListener("load", () => {
  sendScrapedData();

  // Handle dynamic content loading
  const observer = new MutationObserver(() => {
      sendScrapedData();
  });

  observer.observe(document.body, { childList: true, subtree: true });

  setTimeout(() => {
      observer.disconnect();
  }, 10000);
});


// Listen for requests to rescrape
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === "rescrape") {
    sendScrapedData();
  }
});
