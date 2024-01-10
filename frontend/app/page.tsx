import Header from "@/app/components/header";
import ChatSection from "./components/chat-section";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-10 p-5 lg:p-12 background-gradient">
      <Header />
      <ChatSection />
      {/* <a href="tel:+918768775550">Call Kaustubh</a> */}
    </main>
  );
}
