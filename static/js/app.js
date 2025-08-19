// app.js: Funciones de cliente para Mercado Circular

// Token de autorización para operaciones protegidas. 
// Reemplaza con tu propio valor en producción; este valor debe
// coincidir con API_TOKEN en el servidor para permitir la creación
// de productos. Para demostración se lee de localStorage o se
// deja vacío.
const API_TOKEN = localStorage.getItem('apiToken') || '';

/**
 * Carga la lista de productos del servidor y los muestra en
 * el elemento especificado.
 * @param {string} containerId - ID del contenedor donde se insertarán los productos.
 */
function loadProducts(containerId) {
  fetch('/api/products')
    .then((resp) => resp.json())
    .then((products) => {
      const grid = document.getElementById(containerId);
      if (!grid) return;
      grid.innerHTML = '';
      products.forEach((p) => {
        const card = document.createElement('div');
        card.className = 'product';
        const imgSrc = p.image && p.image !== '' ? p.image : 'https://via.placeholder.com/200x150?text=Producto';
        card.innerHTML = `
          <img src="${imgSrc}" alt="${p.name}">
          <h4>${p.name}</h4>
          <p>$${p.price}</p>
          <p>${p.description}</p>
        `;
        grid.appendChild(card);
      });
    })
    .catch((err) => {
      console.error('Error al cargar productos:', err);
    });
}

/**
 * Carga la lista de servicios de reparación desde el servidor y
 * los muestra en el elemento especificado.
 * @param {string} containerId - ID del contenedor donde se insertarán los servicios.
 */
function loadRepairs(containerId) {
  fetch('/api/repairs')
    .then((resp) => resp.json())
    .then((services) => {
      const list = document.getElementById(containerId);
      if (!list) return;
      list.innerHTML = '';
      services.forEach((s) => {
        const item = document.createElement('div');
        item.className = 'repair-item';
        item.innerHTML = `
          <h4>${s.name}</h4>
          <p>${s.description}</p>
          <p><strong>Contacto:</strong> ${s.contact}</p>
        `;
        list.appendChild(item);
      });
    })
    .catch((err) => {
      console.error('Error al cargar servicios:', err);
    });
}

/**
 * Envía un nuevo producto al servidor. Obtiene los datos del
 * formulario y utiliza el token de autorización para la petición.
 * @param {Event} event - El evento de envío de formulario.
 */
function submitProduct(event) {
  event.preventDefault();
  const name = document.getElementById('name').value.trim();
  const description = document.getElementById('description').value.trim();
  const category = document.getElementById('category').value;
  const price = document.getElementById('price').value;
  const image = document.getElementById('image').value.trim();
  const product = { name, description, category, price, image };
  fetch('/api/products', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_TOKEN}`
    },
    body: JSON.stringify(product)
  })
    .then((resp) => {
      if (!resp.ok) {
        return resp.json().then((err) => { throw err; });
      }
      return resp.json();
    })
    .then((data) => {
      alert('Producto publicado correctamente');
      // Redirigir a la página de productos
      window.location.href = 'market.html';
    })
    .catch((err) => {
      console.error('Error al publicar producto:', err);
      alert(err.error || 'No se pudo publicar el producto');
    });
}

// Registrar gestores de eventos comunes cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Cargar productos si hay un contenedor correspondiente
  if (document.getElementById('productGrid')) {
    loadProducts('productGrid');
  }
  // Cargar reparaciones si hay un contenedor
  if (document.getElementById('repairList')) {
    loadRepairs('repairList');
  }
  // Registrar submit del formulario de venta
  const sellForm = document.getElementById('sellForm');
  if (sellForm) {
    sellForm.addEventListener('submit', submitProduct);
  }
});