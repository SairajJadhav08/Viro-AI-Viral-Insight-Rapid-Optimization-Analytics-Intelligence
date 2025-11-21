import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTheme } from 'next-themes';
import { toast } from 'sonner';

// Language translations
const translations: Record<string, Record<string, string>> = {
  en: {
    settings: 'Settings',
    managePreferences: 'Manage your account preferences and system settings',
    notifications: 'Notifications',
    configureUpdates: 'Configure how you receive updates',
    emailNotifications: 'Email Notifications',
    emailDesc: 'Receive email updates about your projects',
    analysisComplete: 'Analysis Complete Alerts',
    analysisDesc: 'Get notified when analysis finishes',
    researchUpdates: 'Research Feed Updates',
    researchDesc: 'Daily digest of new publications',
    displayPreferences: 'Display Preferences',
    customizeInterface: 'Customize your interface',
    theme: 'Theme',
    language: 'Language',
    dataPrivacy: 'Data & Privacy',
    controlData: 'Control your data and privacy settings',
    shareData: 'Share Anonymous Usage Data',
    shareDesc: 'Help improve VIRO-AI',
    exportData: 'Export My Data',
    deleteAccount: 'Delete Account',
  },
  es: {
    settings: 'Configuración',
    managePreferences: 'Administre sus preferencias de cuenta y configuración del sistema',
    notifications: 'Notificaciones',
    configureUpdates: 'Configure cómo recibe actualizaciones',
    emailNotifications: 'Notificaciones por correo electrónico',
    emailDesc: 'Reciba actualizaciones por correo sobre sus proyectos',
    analysisComplete: 'Alertas de análisis completado',
    analysisDesc: 'Reciba notificaciones cuando finalice el análisis',
    researchUpdates: 'Actualizaciones del feed de investigación',
    researchDesc: 'Resumen diario de nuevas publicaciones',
    displayPreferences: 'Preferencias de visualización',
    customizeInterface: 'Personalice su interfaz',
    theme: 'Tema',
    language: 'Idioma',
    dataPrivacy: 'Datos y privacidad',
    controlData: 'Controle su configuración de datos y privacidad',
    shareData: 'Compartir datos de uso anónimos',
    shareDesc: 'Ayude a mejorar VIRO-AI',
    exportData: 'Exportar mis datos',
    deleteAccount: 'Eliminar cuenta',
  },
  fr: {
    settings: 'Paramètres',
    managePreferences: 'Gérez vos préférences de compte et les paramètres du système',
    notifications: 'Notifications',
    configureUpdates: 'Configurez la façon dont vous recevez les mises à jour',
    emailNotifications: 'Notifications par e-mail',
    emailDesc: 'Recevez des mises à jour par e-mail sur vos projets',
    analysisComplete: 'Alertes d\'analyse terminée',
    analysisDesc: 'Soyez notifié lorsque l\'analyse se termine',
    researchUpdates: 'Mises à jour du flux de recherche',
    researchDesc: 'Résumé quotidien des nouvelles publications',
    displayPreferences: 'Préférences d\'affichage',
    customizeInterface: 'Personnalisez votre interface',
    theme: 'Thème',
    language: 'Langue',
    dataPrivacy: 'Données et confidentialité',
    controlData: 'Contrôlez vos paramètres de données et de confidentialité',
    shareData: 'Partager des données d\'utilisation anonymes',
    shareDesc: 'Aidez à améliorer VIRO-AI',
    exportData: 'Exporter mes données',
    deleteAccount: 'Supprimer le compte',
  },
};

export default function Settings() {
  const { theme, setTheme } = useTheme();
  const [language, setLanguage] = useState<string>('en');
  const [mounted, setMounted] = useState(false);

  // Load language from localStorage
  useEffect(() => {
    const savedLanguage = localStorage.getItem('app_language') || 'en';
    setLanguage(savedLanguage);
    setMounted(true);
  }, []);

  // Save language to localStorage
  const handleLanguageChange = (value: string) => {
    setLanguage(value);
    localStorage.setItem('app_language', value);
    toast.success('Language changed successfully');
    // Reload page to apply language changes
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  // Handle theme change
  const handleThemeChange = (value: string) => {
    setTheme(value);
    toast.success(`Theme changed to ${value}`);
  };

  const t = translations[language] || translations.en;

  if (!mounted) {
    return null; // Prevent hydration mismatch
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">{t.settings}</h1>
        <p className="text-muted-foreground">{t.managePreferences}</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t.notifications}</CardTitle>
          <CardDescription>{t.configureUpdates}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="email-notifications">{t.emailNotifications}</Label>
              <p className="text-sm text-muted-foreground">{t.emailDesc}</p>
            </div>
            <Switch id="email-notifications" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="analysis-complete">{t.analysisComplete}</Label>
              <p className="text-sm text-muted-foreground">{t.analysisDesc}</p>
            </div>
            <Switch id="analysis-complete" defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="research-updates">{t.researchUpdates}</Label>
              <p className="text-sm text-muted-foreground">{t.researchDesc}</p>
            </div>
            <Switch id="research-updates" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t.displayPreferences}</CardTitle>
          <CardDescription>{t.customizeInterface}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="theme">{t.theme}</Label>
            <Select value={theme || 'light'} onValueChange={handleThemeChange}>
              <SelectTrigger className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Light</SelectItem>
                <SelectItem value="dark">Dark</SelectItem>
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="language">{t.language}</Label>
            <Select value={language} onValueChange={handleLanguageChange}>
              <SelectTrigger className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Spanish</SelectItem>
                <SelectItem value="fr">French</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t.dataPrivacy}</CardTitle>
          <CardDescription>{t.controlData}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="data-sharing">{t.shareData}</Label>
              <p className="text-sm text-muted-foreground">{t.shareDesc}</p>
            </div>
            <Switch id="data-sharing" />
          </div>
          <div className="pt-4 space-y-2">
            <Button variant="outline" className="w-full">{t.exportData}</Button>
            <Button variant="outline" className="w-full text-red-600 hover:text-red-700">{t.deleteAccount}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}