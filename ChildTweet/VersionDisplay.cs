using System;

namespace ChildTweet
{
    public partial class ChildTweet
    {
        private const string DisplayVersion = "1.21.0";

        private void ApplyVersionToTitle(object sender, EventArgs e)
        {
            Text = $"ChildTweet Ver.{DisplayVersion} [ID:{ID}]";
        }
    }
}
