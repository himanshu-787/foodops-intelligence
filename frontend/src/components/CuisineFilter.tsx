const CUISINES = ["Mughlai", "South Indian", "Italian", "Chinese", "Cafe"];

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export function CuisineFilter({ value, onChange }: Props) {
  return (
    <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Saari cuisines</option>
      {CUISINES.map((c) => (
        <option key={c} value={c}>
          {c}
        </option>
      ))}
    </select>
  );
}