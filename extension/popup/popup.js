document.addEventListener('DOMContentLoaded', function() {
  const imageInput = document.getElementById('imageInput');
  const searchButton = document.getElementById('searchButton');
  const resultsDiv = document.getElementById('results');
  
  // Try both localhost and 127.0.0.1
  const SERVER_URLS = [
    'http://localhost:5000',
    'http://127.0.0.1:5000'
  ];
  
  let serverUrl = SERVER_URLS[0]; // Default to first URL

  // Test server connection on popup load
  testServerConnection();

  searchButton.addEventListener('click', async () => {
    const file = imageInput.files[0];
    if (!file) {
      showError('Please select an image first');
      return;
    }

    // Validate the image format (JPG, PNG, GIF)
    const validFormats = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validFormats.includes(file.type)) {
      showError('Please upload a valid image (JPG, PNG, GIF).');
      return;
    }

    showLoading();

    try {
      const base64Image = await fileToBase64(file);
      console.log(base64Image); // Add this line to verify the Base64 string

      // Try to send request
      let response = null;
      let error = null;
      
      for (const url of SERVER_URLS) {
        try {
          response = await fetch(`${url}/search`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({ image: base64Image })
          });
          
          if (response.ok) {
            serverUrl = url; // Remember working URL
            break;
          }
        } catch (e) {
          error = e;
          console.log(`Failed to connect to ${url}:`, e);
          continue;
        }
      }

      if (!response?.ok) {
        throw error || new Error('Failed to connect to server');
      }

      const results = await response.json();
      displayResults(results);
    } catch (error) {
      showError(`Error: ${error.message}. Please ensure the backend server is running.`);
      console.error('Error:', error);
    }
  });

  async function testServerConnection() {
    let connected = false;
    
    for (const url of SERVER_URLS) {
      try {
        const response = await fetch(`${url}/test`, {
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (response.ok) {
          serverUrl = url;
          connected = true;
          console.log(`Connected successfully to ${url}`);
          break;
        }
      } catch (e) {
        console.log(`Failed to connect to ${url}:`, e);
        continue;
      }
    }

    if (!connected) {
      showError('Cannot connect to server. Please ensure the backend server is running.');
    }
  }

  function showLoading() {
    resultsDiv.innerHTML = `
      <div class="loading">
        <p>Searching for similar products...</p>
        <p class="small">Server URL: ${serverUrl}</p>
      </div>`;
  }

  function showError(message) {
    resultsDiv.innerHTML = `
      <div class="error">
        <p>${message}</p>
        <p class="small">Server URL: ${serverUrl}</p>
      </div>`;
  }

  function displayResults(results) {
    resultsDiv.innerHTML = '';
    
    if (!results || results.length === 0) {
      resultsDiv.innerHTML = '<p>No similar products found.</p>';
      return;
    }

    results.forEach(product => {
      const productCard = document.createElement('div');
      productCard.className = 'product-card';
      productCard.innerHTML = `
        <h3>${product.title || 'Untitled Product'}</h3>
        <p class="product-price">Price: ${product.price || 'N/A'}</p>
        <p>Website: ${product.website || 'Unknown'}</p>
        ${product.url ? `<a href="${product.url}" target="_blank">View Product</a>` : ''}`;
      resultsDiv.appendChild(productCard);
    });
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        let base64String = reader.result;
        // Remove the data URI prefix (e.g., "data:image/jpeg;base64,")
        base64String = base64String.replace(/^data:image\/\w+;base64,/, "");
        resolve(base64String);
      };
      reader.onerror = error => reject(error);
    });
  }
});
