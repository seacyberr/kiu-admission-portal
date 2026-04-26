import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MapPin, ArrowLeft, ArrowRight, Home, Phone } from "lucide-react";
import { motion } from "framer-motion";

// Country codes for phone input
const COUNTRY_CODES = [
  { code: "+256", country: "Uganda", flag: "🇺🇬" },
  { code: "+254", country: "Kenya", flag: "🇰🇪" },
  { code: "+255", country: "Tanzania", flag: "🇹🇿" },
  { code: "+250", country: "Rwanda", flag: "🇷🇼" },
  { code: "+257", country: "Burundi", flag: "🇧🇮" },
  { code: "+243", country: "DR Congo", flag: "🇨🇩" },
  { code: "+260", country: "Zambia", flag: "🇿🇲" },
  { code: "+265", country: "Malawi", flag: "🇲🇼" },
  { code: "+27", country: "South Africa", flag: "🇿🇦" },
  { code: "+234", country: "Nigeria", flag: "🇳🇬" },
  { code: "+233", country: "Ghana", flag: "🇬🇭" },
  { code: "+44", country: "UK", flag: "🇬🇧" },
  { code: "+1", country: "USA/Canada", flag: "🇺🇸" },
  { code: "+91", country: "India", flag: "🇮🇳" },
  { code: "+86", country: "China", flag: "🇨🇳" },
  { code: "+971", country: "UAE", flag: "🇦🇪" },
  { code: "+966", country: "Saudi Arabia", flag: "🇸🇦" },
  { code: "+20", country: "Egypt", flag: "🇪🇬" },
  { code: "+249", country: "Sudan", flag: "🇸🇩" },
  { code: "+252", country: "Somalia", flag: "🇸🇴" },
  { code: "+251", country: "Ethiopia", flag: "🇪🇹" },
  { code: "+253", country: "Djibouti", flag: "🇩🇯" },
  { code: "+225", country: "Côte d'Ivoire", flag: "🇨🇮" },
  { code: "+221", country: "Senegal", flag: "🇸🇳" },
  { code: "+220", country: "Gambia", flag: "🇬🇲" },
  { code: "+232", country: "Sierra Leone", flag: "🇸🇱" },
  { code: "+231", country: "Liberia", flag: "🇱🇷" },
  { code: "+223", country: "Mali", flag: "🇲🇱" },
  { code: "+227", country: "Niger", flag: "🇳🇪" },
  { code: "+235", country: "Chad", flag: "🇹🇩" },
  { code: "+237", country: "Cameroon", flag: "🇨🇲" },
  { code: "+241", country: "Gabon", flag: "🇬🇦" },
  { code: "+242", country: "Congo", flag: "🇨🇬" },
  { code: "+244", country: "Angola", flag: "🇦🇴" },
  { code: "+258", country: "Mozambique", flag: "🇲🇿" },
  { code: "+263", country: "Zimbabwe", flag: "🇿🇼" },
  { code: "+267", country: "Botswana", flag: "🇧🇼" },
  { code: "+264", country: "Namibia", flag: "🇳🇦" },
  { code: "+268", country: "Eswatini", flag: "🇸🇿" },
  { code: "+266", country: "Lesotho", flag: "🇱🇸" },
  { code: "+230", country: "Mauritius", flag: "🇲🇺" },
  { code: "+262", country: "Réunion", flag: "🇷🇪" },
];

// All 135 Uganda districts as of 2024
const UGANDA_DISTRICTS = [
  "Abim", "Adjumani", "Agago", "Alebtong", "Amolatar", "Amudat", "Amuria", "Amuru",
  "Apac", "Arua", "Budaka", "Bududa", "Bugiri", "Bugweri", "Buhweju", "Buikwe",
  "Bukedea", "Bukomansimbi", "Bukwo", "Bulambuli", "Buliisa", "Bundibugyo", "Bunyangabu",
  "Bushenyi", "Busia", "Butaleja", "Butambala", "Butebo", "Buvuma", "Buyende",
  "Dokolo", "Gomba", "Gulu", "Hoima", "Ibanda", "Iganga", "Isingiro", "Jinja",
  "Kaabong", "Kabale", "Kabarole", "Kaberamaido", "Kagadi", "Kakumiro", "Kalaki",
  "Kalangala", "Kaliro", "Kalungu", "Kampala", "Kamuli", "Kamwenge", "Kanungu",
  "Kapchorwa", "Kapelebyong", "Karenga", "Kasanda", "Kasese", "Katakwi", "Kayunga",
  "Kazo", "Kibaale", "Kiboga", "Kibuku", "Kigezi", "Kikuube", "Kiruhura", "Kiryandongo",
  "Kisoro", "Kitagwenda", "Kitgum", "Koboko", "Kole", "Kotido", "Kumi", "Kwania",
  "Kween", "Kyankwanzi", "Kyegegwa", "Kyenjojo", "Kyotera", "Lamwo", "Lira", "Luuka",
  "Luwero", "Lwengo", "Lyantonde", "Manafwa", "Maracha", "Masaka", "Masindi",
  "Mayuge", "Mbale", "Mbarara", "Mitooma", "Mityana", "Moroto", "Moyo", "Mpigi",
  "Mubende", "Mukono", "Nabilatuk", "Nakapiripirit", "Nakaseke", "Nakasongola",
  "Namayingo", "Namisindwa", "Namutumba", "Napak", "Nebbi", "Ngora", "Ntoroko",
  "Ntungamo", "Nwoya", "Obongi", "Omoro", "Otuke", "Oyam", "Pader", "Pakwach",
  "Pallisa", "Rakai", "Rubanda", "Rubirizi", "Rukiga", "Rukungiri", "Rwampara",
  "Sembabule", "Serere", "Sheema", "Sironko", "Soroti", "Terego", "Tororo", "Wakiso",
  "Yumbe", "Zombo"
].sort();

// Validation schema for Step 2
const step2Schema = z.object({
  residentialAddress: z.string().min(5, "Residential address must be at least 5 characters"),
  district: z.string().min(1, "District is required"),
  postalAddress: z.string().optional(),
  emergencyContactName: z.string().min(2, "Emergency contact name is required"),
  emergencyRelationship: z.string().min(1, "Relationship is required"),
  countryCode: z.string().default("+256"),
  emergencyPhone: z.string().regex(/^[0-9]{9}$/, "Phone number must be 9 digits (e.g., 7XX XXX XXX)"),
  emergencyAddress: z.string().min(5, "Emergency contact address is required"),
});

type Step2Data = z.infer<typeof step2Schema>;

interface ContactLocationProps {
  onNext: (data: Step2Data) => void;
  onBack: () => void;
  defaultValues?: Partial<Step2Data>;
}

const relationshipOptions = [
  "Parent",
  "Guardian",
  "Spouse",
  "Sibling",
  "Relative",
  "Friend",
  "Employer",
  "Other"
];

export default function ContactLocation({ onNext, onBack, defaultValues }: ContactLocationProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
    watch,
  } = useForm<Step2Data>({
    resolver: zodResolver(step2Schema),
    defaultValues: {
      residentialAddress: defaultValues?.residentialAddress || "",
      district: defaultValues?.district || "",
      postalAddress: defaultValues?.postalAddress || "",
      emergencyContactName: defaultValues?.emergencyContactName || "",
      emergencyRelationship: defaultValues?.emergencyRelationship || "",
      countryCode: defaultValues?.countryCode || "+256",
      emergencyPhone: defaultValues?.emergencyPhone || "",
      emergencyAddress: defaultValues?.emergencyAddress || "",
    },
  });

  const district = watch("district");
  const emergencyRelationship = watch("emergencyRelationship");
  const countryCode = watch("countryCode");

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-4xl mx-auto"
    >
      <Card className="p-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4 rounded-full bg-primary/10">
            <MapPin className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold">Step 2: Contact & Location Details</h1>
          <p className="mt-2 text-muted-foreground">
            Please provide your contact information.
          </p>
        </div>

        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-primary">Step 2 of 6</span>
            <span className="text-muted-foreground">Contact & Location</span>
          </div>
          <div className="h-2 mt-2 rounded-full bg-muted">
            <div className="h-full w-2/6 rounded-full bg-primary" />
          </div>
        </div>

        <form onSubmit={handleSubmit(onNext)} className="space-y-6">
          {/* Location Section */}
          <div className="p-6 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-4">
              <Home className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold">Residential Address</h2>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="residentialAddress">Residential Address *</Label>
                <Textarea
                  id="residentialAddress"
                  placeholder="e.g., Plot 45, Main Street, Kansanga"
                  {...register("residentialAddress")}
                  className={errors.residentialAddress ? "border-destructive" : ""}
                  rows={3}
                />
                {errors.residentialAddress && (
                  <p className="text-xs text-destructive">{errors.residentialAddress.message}</p>
                )}
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>District *</Label>
                  <Select
                    value={district}
                    onValueChange={(value: string) => setValue("district", value)}
                  >
                    <SelectTrigger className={errors.district ? "border-destructive" : ""}>
                      <SelectValue placeholder="Select district" />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px]">
                      {UGANDA_DISTRICTS.map((dist) => (
                        <SelectItem key={dist} value={dist}>
                          {dist}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.district && (
                    <p className="text-xs text-destructive">{errors.district.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="postalAddress">Postal Address (Optional)</Label>
                  <Input
                    id="postalAddress"
                    placeholder="e.g., P.O. Box 1234, Kampala"
                    {...register("postalAddress")}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Emergency Contact Section */}
          <div className="p-6 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-4">
              <Phone className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold">Emergency Contact</h2>
            </div>
            <p className="mb-4 text-sm text-muted-foreground">
              This person will be contacted in case of emergencies.
            </p>

            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="emergencyContactName">Full Name *</Label>
                  <Input
                    id="emergencyContactName"
                    placeholder="e.g., Jane Doe"
                    {...register("emergencyContactName")}
                    className={errors.emergencyContactName ? "border-destructive" : ""}
                  />
                  {errors.emergencyContactName && (
                    <p className="text-xs text-destructive">{errors.emergencyContactName.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Relationship *</Label>
                  <Select
                    value={emergencyRelationship}
                    onValueChange={(value: string) => setValue("emergencyRelationship", value)}
                  >
                    <SelectTrigger className={errors.emergencyRelationship ? "border-destructive" : ""}>
                      <SelectValue placeholder="Select relationship" />
                    </SelectTrigger>
                    <SelectContent>
                      {relationshipOptions.map((rel) => (
                        <SelectItem key={rel} value={rel}>
                          {rel}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.emergencyRelationship && (
                    <p className="text-xs text-destructive">{errors.emergencyRelationship.message}</p>
                  )}
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="emergencyPhone">Phone Number *</Label>
                  <div className="flex gap-2">
                    <Select
                      value={countryCode}
                      onValueChange={(value: string) => setValue("countryCode", value)}
                    >
                      <SelectTrigger className="w-[140px] shrink-0">
                        <SelectValue placeholder="Code" />
                      </SelectTrigger>
                      <SelectContent className="max-h-[300px]">
                        {COUNTRY_CODES.map((cc) => (
                          <SelectItem key={cc.code} value={cc.code}>
                            <span className="mr-2">{cc.flag}</span>
                            {cc.code} ({cc.country})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input
                      id="emergencyPhone"
                      placeholder="7XX XXX XXX"
                      {...register("emergencyPhone")}
                      className={errors.emergencyPhone ? "border-destructive" : ""}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Selected: {countryCode || "+256"} {watch("emergencyPhone") || ""}
                  </p>
                  {errors.emergencyPhone && (
                    <p className="text-xs text-destructive">{errors.emergencyPhone.message}</p>
                  )}
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="emergencyAddress">Address *</Label>
                  <Textarea
                    id="emergencyAddress"
                    placeholder="e.g., Plot 45, Main Street, Kampala"
                    {...register("emergencyAddress")}
                    className={errors.emergencyAddress ? "border-destructive" : ""}
                    rows={2}
                  />
                  {errors.emergencyAddress && (
                    <p className="text-xs text-destructive">{errors.emergencyAddress.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={onBack}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <Button
              type="submit"
              className="flex items-center gap-2 px-8"
              isLoading={isSubmitting}
            >
              Next Step
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
}
