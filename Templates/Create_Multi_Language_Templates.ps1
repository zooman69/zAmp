# PowerShell script to create multi-language zAmp verification templates
# Creates templates in Spanish, Italian, Hebrew, Dutch, and Portuguese

$languages = @{
    "SPANISH" = @{
        Subject = "Verificacion de la imagen de zAmp y del cable USB"
        Body = @"
<p>Hola,</p>
<br>
<br>
<p>Para diagnosticar con precisi&oacute;n el problema de su zAmp, proporcione fotos claras de los siguientes elementos:</p>
<br>
<p>zAmp:<br>
Una foto de la parte posterior del zAmp, que muestre claramente el n&uacute;mero de serie y el cable USB conectado al zAmp.</p>
<br>
<p>Cable USB Monoprice:<br>
Una foto de primer plano del cable USB Monoprice, enfoc&aacute;ndose en la secci&oacute;n con el logotipo &quot;Monoprice&quot;.</p>
<br>
<p>Configuraci&oacute;n del sistema:<br>
Una foto de la configuraci&oacute;n de su sistema con el cable USB conectado tanto al zAmp como al sistema.</p>
<br>
<p>Consulte la imagen a continuaci&oacute;n para ver ejemplos de las fotos solicitadas. Una vez que haya tomado estas fotos, env&iacute;elas a support@neuroptimal.com.</p>
<br>
<br>
<p>Gracias por su cooperaci&oacute;n.</p>
"@
    }
    "ITALIAN" = @{
        Subject = "Verifica dell'immagine di zAmp e del cavo USB"
        Body = @"
<p>Salve,</p>
<br>
<br>
<p>Per diagnosticare con precisione il problema del vostro zAmp, fornire foto chiare dei seguenti elementi:</p>
<br>
<p>zAmp:<br>
Una foto del retro dello zAmp, che mostri chiaramente il numero di serie e il cavo USB collegato allo zAmp.</p>
<br>
<p>Cavo USB Monoprice:<br>
Una foto ravvicinata del cavo USB Monoprice, concentrandosi sulla sezione con il logo &quot;Monoprice&quot;.</p>
<br>
<p>Configurazione del sistema:<br>
Una foto della configurazione del sistema con il cavo USB collegato sia allo zAmp che al sistema.</p>
<br>
<p>Si prega di fare riferimento all'immagine qui sotto per esempi delle foto richieste. Una volta scattate queste foto, inviarle a support@neuroptimal.com.</p>
<br>
<br>
<p>Grazie per la vostra collaborazione.</p>
"@
    }
    "HEBREW" = @{
        Subject = "אימות תמונת zAmp וכבל USB"
        Body = @"
<p>שלום,</p>
<br>
<br>
<p>כדי לאבחן במדויק את הבעיה של ה-zAmp שלך, אנא ספק תמונות ברורות של הפריטים הבאים:</p>
<br>
<p>zAmp:<br>
תמונה של החלק האחורי של ה-zAmp, המציגה בבירור את המספר הסידורי ואת כבל ה-USB המחובר ל-zAmp.</p>
<br>
<p>כבל USB Monoprice:<br>
תמונת תקריב של כבל ה-USB Monoprice, תוך התמקדות בחלק עם הלוגו &quot;Monoprice&quot;.</p>
<br>
<p>תצורת המערכת:<br>
תמונה של תצורת המערכת שלך עם כבל ה-USB מחובר גם ל-zAmp וגם למערכת.</p>
<br>
<p>אנא עיין בתמונה למטה לדוגמאות של התמונות המבוקשות. לאחר שצילמת את התמונות הללו, שלח אותן אל support@neuroptimal.com.</p>
<br>
<br>
<p>תודה על שיתוף הפעולה שלך.</p>
"@
    }
    "DUTCH" = @{
        Subject = "Verificatie van zAmp afbeelding en USB-kabel"
        Body = @"
<p>Hallo,</p>
<br>
<br>
<p>Om het probleem met uw zAmp nauwkeurig te diagnosticeren, gelieve duidelijke foto's te verstrekken van de volgende items:</p>
<br>
<p>zAmp:<br>
Een foto van de achterkant van de zAmp, waarop duidelijk het serienummer en de USB-kabel die op de zAmp is aangesloten te zien zijn.</p>
<br>
<p>Monoprice USB-kabel:<br>
Een close-upfoto van de Monoprice USB-kabel, met de nadruk op het gedeelte met het &quot;Monoprice&quot;-logo.</p>
<br>
<p>Systeemconfiguratie:<br>
Een foto van uw systeemconfiguratie met de USB-kabel aangesloten op zowel de zAmp als het systeem.</p>
<br>
<p>Raadpleeg de onderstaande afbeelding voor voorbeelden van de gevraagde foto's. Zodra u deze foto's heeft gemaakt, stuurt u ze naar support@neuroptimal.com.</p>
<br>
<br>
<p>Dank u voor uw medewerking.</p>
"@
    }
    "PORTUGUESE" = @{
        Subject = "Verificacao da imagem do zAmp e do cabo USB"
        Body = @"
<p>Ol&aacute;,</p>
<br>
<br>
<p>Para diagnosticar com precis&atilde;o o problema do seu zAmp, forne&ccedil;a fotos claras dos seguintes itens:</p>
<br>
<p>zAmp:<br>
Uma foto da parte traseira do zAmp, mostrando claramente o n&uacute;mero de s&eacute;rie e o cabo USB conectado ao zAmp.</p>
<br>
<p>Cabo USB Monoprice:<br>
Uma foto em close do cabo USB Monoprice, focando na se&ccedil;&atilde;o com o logotipo &quot;Monoprice&quot;.</p>
<br>
<p>Configura&ccedil;&atilde;o do sistema:<br>
Uma foto da configura&ccedil;&atilde;o do seu sistema com o cabo USB conectado tanto ao zAmp quanto ao sistema.</p>
<br>
<p>Consulte a imagem abaixo para exemplos das fotos solicitadas. Depois de tirar essas fotos, envie-as para support@neuroptimal.com.</p>
<br>
<br>
<p>Obrigado pela sua coopera&ccedil;&atilde;o.</p>
"@
    }
}

try {
    $outlook = New-Object -ComObject Outlook.Application
    $imagePath = "c:\WhisperProject\zAmp\Images\zAmp verification"

    foreach ($lang in $languages.Keys) {
        Write-Host "Creating $lang template..."

        # Create a new mail item
        $mail = $outlook.CreateItem(0)

        # Set subject (without accents for now - will be manually updated)
        $mail.Subject = $languages[$lang].Subject

        # Create HTML body
        $htmlBody = @"
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<meta charset="UTF-8">
</head>
<body style="font-family: 'Open Sans', Arial, sans-serif; font-size: 11pt;">
$($languages[$lang].Body)
</body>
</html>
"@

        $mail.HTMLBody = $htmlBody

        # Add verification image as embedded attachment
        if (Test-Path $imagePath) {
            $attachment = $mail.Attachments.Add($imagePath)
            # Set the attachment as inline/embedded
            $attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "zAmpVerificationImage")

            # Also add directly to HTML body with the embedded image
            $mail.HTMLBody = $mail.HTMLBody.Replace("</body>", "<p><img src=`"cid:zAmpVerificationImage`" alt=`"zAmp Verification`" style=`"max-width: 100%; height: auto;`"></p></body>")
        }

        # Save as MSG file
        $savePath = "c:\WhisperProject\zAmp\Templates\zAmp and USB Cable Verification - $lang.msg"
        $mail.SaveAs($savePath, 3)

        Write-Host "  Created: $savePath"

        # Clean up
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($mail) | Out-Null
    }

    Write-Host "`nAll templates created successfully!"
    Write-Host "`nNOTE: Subject lines may need manual correction for special characters."
    Write-Host "Please open each template and verify the subject line displays correctly."

} catch {
    Write-Host "Error: $($_.Exception.Message)"
} finally {
    if ($outlook) {
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($outlook) | Out-Null
    }
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
