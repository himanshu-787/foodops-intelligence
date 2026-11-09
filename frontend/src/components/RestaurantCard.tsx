export type Restaurant = {
  id: number;
  name: string;
  cuisine: string;
  rating: number;
  is_veg: boolean;
};

export function RestaurantCard({ restaurant }: { restaurant: Restaurant }) {
  return (
    <div className="card">
      <h3>{restaurant.name}</h3>
      <p>
        <span className="tag">{restaurant.cuisine}</span>{" "}
        {restaurant.is_veg ? "🟢 Veg" : "🔴 Non-veg"}
      </p>
      <p>⭐ {restaurant.rating}</p>
      {restaurant.rating >= 4.5 && <p>🔥 Top rated</p>}
    </div>
  );
}