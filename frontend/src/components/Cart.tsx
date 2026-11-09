import type { MenuItem } from "./MenuList";

export type CartLine = { item: MenuItem; quantity: number };

type Props = {
  lines: CartLine[];
  placing: boolean;
  message: string | null;
  error: string | null;
  loggedIn: boolean;
  onChangeQty: (itemId: number, delta: number) => void;
  onPlaceOrder: () => void;
};

export function Cart({ lines, placing, message, error, loggedIn, onChangeQty, onPlaceOrder }: Props) {
  // Derived data: state nahi, har render par calculate
  const total = lines.reduce((sum, l) => sum + l.item.price * l.quantity, 0);

  return (
    <div className="card cart">
      <h3>🛒 Cart</h3>
      {lines.length === 0 && <p>Cart khaali hai</p>}

      {lines.map((l) => (
        <div className="cart-line" key={l.item.id}>
          <span>{l.item.name}</span>
          <span>
            <button className="qty" onClick={() => onChangeQty(l.item.id, -1)}>-</button>
            {" "}{l.quantity}{" "}
            <button className="qty" onClick={() => onChangeQty(l.item.id, 1)}>+</button>
          </span>
          <span>₹{l.item.price * l.quantity}</span>
        </div>
      ))}

      {lines.length > 0 && <p><b>Total: ₹{total}</b></p>}

      {!loggedIn && lines.length > 0 && <p className="error">Order ke liye pehle login karo</p>}
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <button
        className="btn"
        disabled={lines.length === 0 || placing || !loggedIn}
        onClick={onPlaceOrder}
      >
        {placing ? "Order ho raha hai..." : "Place Order"}
      </button>
    </div>
  );
}