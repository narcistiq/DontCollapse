import re

with open("app/dashboard/page.tsx", "r") as f:
    content = f.read()

typewriter_code = """
const TypewriterText = ({ text }: { text: string }) => {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(prev => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, 15);
    return () => clearInterval(timer);
  }, [text]);
  return <span>{displayed}</span>;
}

"""
if 'const TypewriterText' not in content:
    content = content.replace('export default function DashboardPage() {', typewriter_code + 'export default function DashboardPage() {')

with open("app/dashboard/page.tsx", "w") as f:
    f.write(content)

