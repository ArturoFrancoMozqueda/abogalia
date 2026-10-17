import { ProfessionalDraft } from "../components/professional-draft";
export function meta() {
  return [
    { title: "Mis contextos profesionales | Legalia" },
    { name: "robots", content: "noindex, nofollow" },
    { name: "referrer", content: "no-referrer" },
  ];
}
export default function ProfessionalContexts() {
  return <ProfessionalDraft contextsOnly />;
}
