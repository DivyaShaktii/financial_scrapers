export default function YearFilter({ setYears }) {
  return (
    <select onChange={(e) => setYears(e.target.value)}>
      <option value="5">5 Years</option>
      <option value="3">3 Years</option>
      <option value="1">1 Year</option>
    </select>
  );
}