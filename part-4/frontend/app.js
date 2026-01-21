const API_URL = "http://localhost:5000/api/books";

// DOM Elements
const booksTable = document.getElementById("booksTable");
const authorsTable = document.getElementById("authorsTable");
const addBtn = document.getElementById("addBtn");
//const searchBtn = document.getElementById("searchBtn");
//const resetBtn = document.getElementById("resetBtn");
const addAuthorBtn = document.getElementById("addAuthorBtn");

const updateAuthorBtn = document.getElementById("updateAuthorBtn");

let editingAuthorId = null;


let editingBookId = null;
const updateBtn = document.getElementById("updateBtn");

// Author dropdown
const authorSelect = document.getElementById("author_id");



// Load books on page load
document.addEventListener("DOMContentLoaded", () => {
  loadBooks();
  loadAuthors();
});


// ==========================
// FETCH ALL BOOKS
// ==========================
function loadBooks() {
  fetch(API_URL)
    .then(res => res.json())
    .then(data => {
      booksTable.innerHTML = "";

      data.books.forEach(book => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${book.id}</td>
          <td>${book.title}</td>
          <td>${book.author || ""}</td>
          <td>${book.year || ""}</td>
          <td>
             <button onclick="editBook(${book.id}, '${book.title}', ${book.author_id}, ${book.year || ''}, '${book.isbn || ''}')">✏️</button>
            <button onclick="deleteBook(${book.id})">❌</button>
          </td>
        `;

        booksTable.appendChild(row);
      });
    });
}

function loadAuthors() {
  fetch("http://localhost:5000/api/authors")
    .then(res => res.json())
    .then(data => {
      authorSelect.innerHTML = '<option value="">Select Author</option>';

      data.authors.forEach(author => {
        const option = document.createElement("option");
        option.value = author.id;
        option.textContent = author.name;
        authorSelect.appendChild(option);
      });
    });
}

function loadAuthorsList() {
  fetch("http://localhost:5000/api/authors")
    .then(res => res.json())
    .then(data => {
      authorsTable.innerHTML = "";

      data.authors.forEach(author => {
        authorsTable.innerHTML += `
          <tr>
            <td>${author.id}</td>
            <td>${author.name}</td>
            <td>${author.city || ""}</td>
            <td>
              <button onclick="editAuthor(${author.id}, '${author.name}', '${author.city || ""}')">✏️</button>
              <button onclick="deleteAuthor(${author.id})">❌</button>
            </td>
          </tr>
        `;
      });
    });
}

function deleteAuthor(id) {
  fetch(`http://localhost:5000/api/authors/${id}`, {
    method: "DELETE"
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) alert(data.error);
    loadAuthorsList();
    loadAuthors(); // refresh dropdown
  });
}
function editAuthor(id, name, city) {
  document.getElementById("authorName").value = name;
  document.getElementById("authorCity").value = city;

  editingAuthorId = id;
  updateAuthorBtn.disabled = false;
  addAuthorBtn.disabled = true;
}


function addAuthor() {
  const name = document.getElementById("authorName").value;
  const city = document.getElementById("authorCity").value;

  if (!name) {
    alert("Author name is required");
    return;
  }

  fetch("http://localhost:5000/api/authors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, city })
  })
  .then(res => res.json())
  .then(() => {
    document.getElementById("authorName").value = "";
    document.getElementById("authorCity").value = "";
    loadAuthors();   // refresh dropdown
    alert("Author added successfully");
  });
}



// ==========================
// ADD BOOK
// ==========================
addBtn.addEventListener("click", () => {
  const titleVal = document.getElementById("title").value.trim();
  const authorIdVal = document.getElementById("author_id").value;
  const yearVal = document.getElementById("year").value;
  const isbnVal = document.getElementById("isbn").value;

  if (!titleVal) {
    alert("Title is required");
    return;
  }

  if (!authorIdVal) {
    alert("Please select an author");
    return;
  }

  fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: titleVal,
      author_id: Number(authorIdVal), // ✅ IMPORTANT
      year: yearVal,
      isbn: isbnVal
    })
  })
  .then(res => res.json())
  .then(data => {
    if (!data.success) {
      alert(data.error);
      return;
    }
    clearInputs();
    loadBooks();
  })
  .catch(err => {
    console.error("Add book failed:", err);
  });
});

addAuthorBtn.addEventListener("click", () => {
  const name = authorName.value;
  const city = authorCity.value;

  if (!name) return alert("Author name required");

  fetch("http://localhost:5000/api/authors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, city })
  }).then(() => {
    authorName.value = "";
    authorCity.value = "";
    loadAuthorsList();
    loadAuthors();
  });
});

updateBtn.addEventListener("click", () => {
  fetch(`${API_URL}/${editingBookId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: document.getElementById("title").value,
      author_id: Number(document.getElementById("author_id").value),
      year: document.getElementById("year").value,
      isbn: document.getElementById("isbn").value
    })
  })
  .then(() => {
    clearInputs();
    loadBooks();
    editingBookId = null;
    updateBtn.disabled = true;
    addBtn.disabled = false;
  });
});


// ==========================
// DELETE BOOK
// ==========================
function deleteBook(id) {
  fetch(`${API_URL}/${id}`, {
    method: "DELETE"
  })
  .then(() => loadBooks());
}

function editBook(id, title, author_id, year, isbn) {
  document.getElementById("title").value = title;
  authorSelect.value = author_id;
  document.getElementById("year").value = year;
  document.getElementById("isbn").value = isbn;

  editingBookId = id;
  updateBtn.disabled = false;
  addBtn.disabled = true;
}



// ==========================
// SEARCH BOOKS
// ==========================
// searchBtn.addEventListener("click", () => {
//   const q = document.getElementById("searchInput").value;

//   fetch(`${API_URL}/search?q=${q}`)
//     .then(res => res.json())
//     .then(data => {
//       booksTable.innerHTML = "";

//       data.books.forEach(book => {
//         const row = document.createElement("tr");
//         row.innerHTML = `
//           <td>${book.id}</td>
//           <td>${book.title}</td>
//           <td>${book.author || ""}</td>
//           <td>${book.year || ""}</td>
//           <td>
//             <button onclick="deleteBook(${book.id})">❌</button>
//           </td>
//         `;
//         booksTable.appendChild(row);
//       });
//     });
//});

// ==========================
// RESET SEARCH
// ==========================
// resetBtn.addEventListener("click", loadBooks);
// addAuthorBtn.addEventListener("click", addAuthor);


// ==========================
// HELPERS
// ==========================
function clearInputs() {
  document.getElementById("title").value = "";
  document.getElementById("author_id").value = "";
  document.getElementById("year").value = "";
  document.getElementById("isbn").value = "";
}
function showBooks() {
  document.getElementById("booksPage").style.display = "block";
  document.getElementById("authorsPage").style.display = "none";
}

function showAuthors() {
  document.getElementById("booksPage").style.display = "none";
  document.getElementById("authorsPage").style.display = "block";
  loadAuthorsList(); 
}


// Default page
showBooks();
