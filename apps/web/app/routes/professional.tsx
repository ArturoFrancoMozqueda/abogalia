import { ProfessionalDraft } from "../components/professional-draft";
export function meta() {
  return [
    { title: "Mi perfil profesional | Legalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}
export default function Professional() {
  return <ProfessionalDraft />;
}
