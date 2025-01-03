// Crear el mapa
const map = L.map('map', {
    center: [41.5, 2.0], // Ajusta les coordenades segons la regió
    zoom: 8,
    zoomControl: true,
    attributionControl: false,
    maxBounds: [[-90, -180], [90, 180]], // Limita la vista
    maxBoundsViscosity: 1.0 // Evita moure's fora dels límits
});

// Añadir un fondo de mapa
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Crear una capa de fons llis per al mar
L.rectangle([[-90, -180], [90, 180]], {
    color: '#336699', // Color del mar
    fillColor: '#336699',
    fillOpacity: 1
}).addTo(map);

// Càrrega del JSON de comarques
let geoLayer;
let comarcaNames = []; // Array per guardar els noms de les comarques
let revealedLayers = []; // Array per mantenir les comarques revelades
fetch('divisions-administratives-v2r1-comarques-250000-20240705.json')
    .then(response => response.json())
    .then(data => {
        // Crear una capa geoJSON sense afegir-la directament al mapa
        geoLayer = L.geoJSON(data, {
            style: feature => ({
                color: '#2c3e50', // Color del contorn
                weight: 1,
                fillColor: '#95a5a6', // Color de la terra
                fillOpacity: 0.7
            }),
            onEachFeature: (feature, layer) => {
                // Afegeix un ID únic per a cada comarca
                layer.options.id = feature.properties.CODICOMAR;

                // Guardar el nom de la comarca
                comarcaNames.push({ name: feature.properties.NOMCOMAR, layer });

                // Afegir interactivitat amb "hover"
                layer.on('mouseover', () => {
                    if (!revealedLayers.includes(layer)) {
                        layer.setStyle({
                            weight: 2,
                            fillOpacity: 0.8
                        });
                    }
                });

                layer.on('mouseout', () => {
                    if (!revealedLayers.includes(layer)) {
                        layer.setStyle({
                            weight: 1,
                            fillOpacity: 0.7
                        });
                    }
                });

                // Vincular el popup amb informació de la comarca
                layer.bindPopup(`<strong>${feature.properties.NOMCOMAR}</strong><br>Àrea: ${feature.properties.AREAC5000} km²`);
            }
        });

        // Seleccionar dues comarques inicials (només aquestes es mostraran inicialment)
        const shuffledComarcas = comarcaNames.sort(() => 0.5 - Math.random());
        const selectedComarcas = shuffledComarcas.slice(0, 2);

        selectedComarcas.forEach((comarca, index) => {
            const color = index === 0 ? '#00ff00' : '#ff0000'; // Verd per la primera, vermell per la segona
            comarca.layer.setStyle({
                weight: 2,
                fillColor: color,
                fillOpacity: 0.9
            });
            map.addLayer(comarca.layer);
            revealedLayers.push(comarca.layer);
        });

        // Ajustar límits inicials només a les dues comarques seleccionades
        const bounds = L.latLngBounds(selectedComarcas.map(c => c.layer.getBounds()));
        map.fitBounds(bounds);
    })
    .catch(error => console.error('Error al carregar el JSON:', error));

// Afegir una barra de cerca amb un botó de validar
const searchDiv = document.createElement('div');
searchDiv.innerHTML = `
    <div style="position: absolute; top: 10px; left: 10px; z-index: 1000;">
        <input id="searchBar" type="text" placeholder="Cerca una comarca..." style="padding: 5px;" autocomplete="off">
        <button id="validateButton" style="padding: 5px;">Validar</button>
        <ul id="suggestions" style="list-style: none; margin: 0; padding: 0; background: white; border: 1px solid #ccc; position: absolute; top: 30px; left: 0; width: calc(100% - 10px); display: none;"></ul>
    </div>
`;
document.body.appendChild(searchDiv);

const searchBar = document.getElementById('searchBar');
const suggestions = document.getElementById('suggestions');

// Mostrar suggeriments mentre s'escriu
searchBar.addEventListener('input', () => {
    const query = searchBar.value.toLowerCase();
    suggestions.innerHTML = '';
    if (query.length >= 3) { // Només mostrar suggeriments si la longitud és de 3 o més lletres
        const matches = comarcaNames.filter(comarca => comarca.name.toLowerCase().includes(query));
        matches.forEach(match => {
            const suggestionItem = document.createElement('li');
            suggestionItem.textContent = match.name;
            suggestionItem.style.padding = '5px';
            suggestionItem.style.cursor = 'pointer';
            suggestionItem.addEventListener('click', () => {
                searchBar.value = match.name;
                suggestions.style.display = 'none';
            });
            suggestions.appendChild(suggestionItem);
        });
        suggestions.style.display = 'block';
    } else {
        suggestions.style.display = 'none';
    }
});

// Amagar els suggeriments quan es fa clic fora
document.addEventListener('click', (event) => {
    if (!searchDiv.contains(event.target)) {
        suggestions.style.display = 'none';
    }
});

// Validar la cerca i afegir la comarca seleccionada
document.getElementById('validateButton').addEventListener('click', () => {
    const query = searchBar.value.toLowerCase();
    let found = false;

    if (geoLayer) {
        let bestMatch = null;
        let bestSimilarity = 0.8; // Umbral mínim de similitud

        geoLayer.eachLayer(layer => {
            const comarcaName = layer.feature.properties.NOMCOMAR.toLowerCase();
            const similarity = calculateSimilarity(comarcaName, query);
            if (similarity > bestSimilarity) {
                bestMatch = layer;
                bestSimilarity = similarity;
            }
        });

        if (bestMatch) {
            if (revealedLayers.includes(bestMatch)) {
                alert('Aquesta comarca ja ha estat seleccionada.');
            } else {
                found = true;
                map.addLayer(bestMatch);
                revealedLayers.push(bestMatch);

                // Marcar les comarques adjacents de forma transitiva
                highlightAdjacent(bestMatch);
            }
        }
    }

    if (!found) {
        alert('No hi ha cap comarca que coincideixi amb aquesta cerca.');
    }

    // Netejar la barra de cerca
    searchBar.value = '';
    suggestions.style.display = 'none';
});

// Funció recursiva per marcar comarques adjacents
function highlightAdjacent(layer, color = '#00ff0066', visited = new Set()) {
    if (visited.has(layer)) return; // Evitar processar la mateixa capa diverses vegades
    visited.add(layer);

    geoLayer.eachLayer(otherLayer => {
        if (areLayersAdjacent(layer, otherLayer) && !revealedLayers.includes(otherLayer)) {
            otherLayer.setStyle({
                fillColor: color, // Verd transparent
                fillOpacity: 0.6
            });

            // Afegir al mapa i a la llista de comarques revelades
            map.addLayer(otherLayer);
            revealedLayers.push(otherLayer);

            // Comprovar comarques adjacents de forma transitiva
            highlightAdjacent(otherLayer, color, visited);
        }
    });
}

// Funció per determinar si dues capes són adjacents
function areLayersAdjacent(layer1, layer2) {
    const bounds1 = layer1.getBounds();
    const bounds2 = layer2.getBounds();
    return bounds1.intersects(bounds2);
}

// Funció per calcular semblança entre cadenes
function calculateSimilarity(str1, str2) {
    const levenshtein = (a, b) => {
        const matrix = Array.from({ length: a.length + 1 }, () => []);
        for (let i = 0; i <= a.length; i++) matrix[i][0] = i;
        for (let j = 0; j <= b.length; j++) matrix[0][j] = j;
        for (let i = 1; i <= a.length; i++) {
            for (let j = 1; j <= b.length; j++) {
                const cost = a[i - 1] === b[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j - 1] + cost
                );
            }
        }
        return matrix[a.length][b.length];
    };
    return 1 - levenshtein(str1.toLowerCase(), str2.toLowerCase()) / Math.max(str1.length, str2.length);
}
