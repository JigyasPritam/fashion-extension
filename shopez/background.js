let productData = [];

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "sendProducts") {
    productData = message.data;
    console.log("Product data received in background:", productData);
    sendResponse({ status: "success" });
  } else if (message.action === "getProducts") {
    console.log("Sending product data to popup:", productData);
    sendResponse({ products: productData });
  }
});

