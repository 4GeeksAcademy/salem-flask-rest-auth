// API functions for interacting with the backend
const BASE_URL = '/api';

// Authentication API functions
export const loginUser = async (email, password) => {
  try {
    const response = await fetch(`${BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.msg || 'Login failed');
    }
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

// No logout endpoint in backend, so just clear local storage/token if needed
export const logoutUser = async () => {
  // Implement client-side logout if needed
  return { msg: 'Logged out (client only)' };
};

export const getCurrentUser = async (token) => {
  try {
    const response = await fetch(`${BASE_URL}/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      return null; // Not authenticated
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Get current user error:', error);
    return null;
  }
};

export const fetchVehicles = async () => {
  try {
    const res = await fetch("/api/vehicles");
    const vehicles = await res.json();
    return vehicles.map(vehicle => ({
      uid: vehicle.id.toString(),
      id: vehicle.id,
      name: vehicle.name,
      model: vehicle.model,
      manufacturer: vehicle.manufacturer,
      image_url: vehicle.image_url,
      type: "vehicle"
    }));
  } catch (error) {
    console.error("Error fetching vehicles:", error);
    return [];
  }
};

export const fetchPeople = async () => {
  try {
    const res = await fetch("/api/people");
    const people = await res.json();
    return people.map(person => ({
      uid: person.id.toString(),
      id: person.id,
      name: person.name,
      gender: person.gender,
      birthYear: person.birth_year,
      image_url: person.image_url,
      type: "character"
    }));
  } catch (error) {
    console.error("Error fetching people:", error);
    return [];
  }
};

export const fetchPlanets = async () => {
  try {
    const res = await fetch("/api/planets");
    const planets = await res.json();
    return planets.map(planet => ({
      uid: planet.id.toString(),
      id: planet.id,
      name: planet.name,
      climate: planet.climate,
      population: planet.population,
      image_url: planet.image_url,
      type: "planet"
    }));
  } catch (error) {
    console.error("Error fetching planets:", error);
    return [];
  }
};

export const getStarWarsData = async () => {
  const [characters, planets, vehicles] = await Promise.all([
    fetchPeople(),
    fetchPlanets(),
    fetchVehicles()
  ]);
  console.log("getStarWarsData result:", { characters, planets, vehicles });
  return { characters, planets, vehicles };
};

// Favorites API functions
export const getFavorites = async () => {
  try {
    const res = await fetch("/api/users/favorites", {
      credentials: 'include'
    });
    
    if (!res.ok) {
      throw new Error('Authentication required');
    }
    
    const backendFavorites = await res.json();
    
    // Transform backend format to frontend format
    const frontendFavorites = backendFavorites.map(fav => {
      if (fav.people) {
        return {
          uid: fav.people.id.toString(),
          id: fav.people.id,
          name: fav.people.name,
          gender: fav.people.gender,
          birthYear: fav.people.birth_year,
          image_url: fav.people.image_url,
          type: "character"
        };
      } else if (fav.planet) {
        return {
          uid: fav.planet.id.toString(),
          id: fav.planet.id,
          name: fav.planet.name,
          climate: fav.planet.climate,
          population: fav.planet.population,
          image_url: fav.planet.image_url,
          type: "planet"
        };
      } else if (fav.vehicle) {
        return {
          uid: fav.vehicle.id.toString(),
          id: fav.vehicle.id,
          name: fav.vehicle.name,
          model: fav.vehicle.model,
          manufacturer: fav.vehicle.manufacturer,
          image_url: fav.vehicle.image_url,
          type: "vehicle"
        };
      }
      return null;
    }).filter(Boolean); // Remove any null entries
    
    return frontendFavorites;
  } catch (error) {
    console.error("Error fetching favorites:", error);
    throw error;
  }
};


// Add favorite using backend /api/favorites POST
export const addFavorite = async (type, id, token) => {
  try {
    const typeMap = {
      character: 'people_id',
      planet: 'planet_id',
      vehicle: 'vehicle_id'
    };
    const body = { [typeMap[type]]: id };
    const res = await fetch(`/api/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.msg || 'Failed to add favorite');
    }
    return await res.json();
  } catch (error) {
    console.error("Error adding favorite:", error);
    throw error;
  }
};

// Remove favorite using backend /api/favorites/<id> DELETE
export const removeFavorite = async (favoriteId, token) => {
  try {
    const res = await fetch(`/api/favorites/${favoriteId}`, {
      method: "DELETE",
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      }
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.msg || 'Failed to remove favorite');
    }
    return await res.json();
  } catch (error) {
    console.error("Error removing favorite:", error);
    throw error;
  }
};

