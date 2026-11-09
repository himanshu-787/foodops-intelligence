type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function SearchBar({ value, onChange }: Props) {
  return (
    <input
      className="input"
      placeholder="Restaurant search karo (min 2 akshar)"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}