import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { MapPin, ArrowLeft, ArrowRight, Home, Phone, Heart } from "lucide-react";
import { motion } from "framer-motion";

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
  emergencyPhone: z.string().regex(/^(\+256|0)[0-9]{9}$/, "Invalid phone number format. Use +2567XX XXX XXX or 07XX XXX XXX"),
  emergencyAddress: z.string().min(5, "Emergency contact address is required"),
  sponsorshipType: z.enum(["bursary", "private"], {
    required_error: "Please select a sponsorship type",
  }),
  sponsorshipSource: z.string().optional(), // Only for private sponsorship
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
      emergencyPhone: defaultValues?.emergencyPhone || "",
      emergencyAddress: defaultValues?.emergencyAddress || "",
      sponsorshipType: defaultValues?.sponsorshipType || undefined,
      sponsorshipSource: defaultValues?.sponsorshipSource || "",
    },
  });

  const district = watch("district");
  const emergencyRelationship = watch("emergencyRelationship");
  const sponsorshipType = watch("sponsorshipType");

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
            Please provide your contact information and sponsorship details.
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
                    onValueChange={(value) => setValue("district", value)}
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
                    onValueChange={(value) => setValue("emergencyRelationship", value)}
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
                  <Input
                    id="emergencyPhone"
                    placeholder="e.g., +256 7XX XXX XXX"
                    {...register("emergencyPhone")}
                    className={errors.emergencyPhone ? "border-destructive" : ""}
                  />
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

          {/* Sponsorship Section */}
          <div className="p-6 rounded-lg bg-muted/50">
            <div className="flex items-center gap-2 mb-4">
              <Heart className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold">Sponsorship Details</h2>
            </div>
            <p className="mb-4 text-sm text-muted-foreground">
              Select how your tuition fees will be covered.
            </p>

            <div className="space-y-4">
              <div className="space-y-3">
                <Label>Sponsorship Type *</Label>
                <RadioGroup
                  value={sponsorshipType}
                  onValueChange={(value: "bursary" | "private") => setValue("sponsorshipType", value)}
                  className="grid gap-4 md:grid-cols-2"
                >
                  <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    sponsorshipType === "bursary" 
                      ? "border-primary bg-primary/5" 
                      : "border-muted hover:border-primary/50"
                  }`}>
                    <RadioGroupItem value="bursary" id="bursary" className="sr-only" />
                    <Label htmlFor="bursary" className="cursor-pointer">
                      <div className="font-semibold">KIU Bursary</div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        50% tuition coverage (merit/need-based)
                      </p>
                    </Label>
                  </div>

                  <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    sponsorshipType === "private" 
                      ? "border-primary bg-primary/5" 
                      : "border-muted hover:border-primary/50"
                  }`}>
                    <RadioGroupItem value="private" id="private" className="sr-only" />
                    <Label htmlFor="private" className="cursor-pointer">
                      <div className="font-semibold">Private Sponsorship</div>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Full tuition payment (any source)
                      </p>
                    </Label>
                  </div>
                </RadioGroup>
                {errors.sponsorshipType && (
                  <p className="text-xs text-destructive">{errors.sponsorshipType.message}</p>
                )}
              </div>

              {sponsorshipType === "private" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="space-y-2"
                >
                  <Label htmlFor="sponsorshipSource">Sponsorship Source (Optional)</Label>
                  <Select
                    value={watch("sponsorshipSource")}
                    onValueChange={(value) => setValue("sponsorshipSource", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select source (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Parent/Guardian">Parent/Guardian</SelectItem>
                      <SelectItem value="Self">Self</SelectItem>
                      <SelectItem value="Employer">Employer</SelectItem>
                      <SelectItem value="NGO">NGO</SelectItem>
                      <SelectItem value="Organization">Organization</SelectItem>
                      <SelectItem value="Other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </motion.div>
              )}
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
