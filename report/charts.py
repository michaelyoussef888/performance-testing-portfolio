import pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
B="#1F3A5F"; O="#D9822B"; G="#2E8B57"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.spines.top":False,"axes.spines.right":False})
def hist(f):
    d=pd.read_csv(f"results/{f}_stats_history.csv"); a=d[d.Name=="Aggregated"].copy()
    a["t"]=a.Timestamp-a.Timestamp.min(); a=a[a["User Count"]>0]
    for c in ["95%","50%"]: a[c]=pd.to_numeric(a[c],errors="coerce")
    return a
b,t=hist("baseline"),hist("tuned")
def overtime(a,name,fn,loc="upper left"):
    fig,ax=plt.subplots(figsize=(7.2,2.8)); ax2=ax.twinx()
    ax2.fill_between(a.t,a["User Count"],color="#cfd8e3",alpha=.6,lw=0,label="Virtual users"); ax2.set_ylabel("Virtual users",color="#7a8899"); ax2.spines["top"].set_visible(False)
    ax.set_zorder(ax2.get_zorder()+1); ax.patch.set_visible(False)
    ax.plot(a.t,a["95%"].rolling(5,min_periods=1).median(),color=O,lw=1.8,label="p95 response time")
    ax.plot(a.t,a["50%"].rolling(5,min_periods=1).median(),color=B,lw=1.4,label="Median response time")
    ax.set_xlabel("Elapsed time (s)"); ax.set_ylabel("Response time (ms)"); ax.set_title(name,loc="left",fontsize=10,fontweight="bold")
    h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels(); ax.legend(h1+h2,l1+l2,loc=loc,frameon=True,framealpha=.9,edgecolor="none",fontsize=8)
    fig.tight_layout(); fig.savefig(fn,dpi=200); plt.close(fig)
overtime(b,"Baseline: response time under step load","report/c1_baseline_rt.png")
overtime(t,"After tuning: response time under the same load","report/c2_tuned_rt.png",loc="lower right")
fig,ax=plt.subplots(figsize=(7.2,2.6))
for a,n,c in [(b,"Baseline",O),(t,"After tuning",G)]:
    g=a.groupby("User Count")["Requests/s"].median(); g=g[g.index.isin([50,100,200,300])]
    ax.plot(g.index,g.values,marker="o",color=c,lw=1.8,label=n)
ax.plot([50,300],[40,240],ls=":",color="#999",lw=1,label="Linear scaling")
ax.set_xlabel("Virtual users"); ax.set_ylabel("Throughput (req/s)"); ax.set_title("Throughput vs. load: the saturation point",loc="left",fontsize=10,fontweight="bold"); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig("report/c3_throughput.png",dpi=200); plt.close(fig)
sb=pd.read_csv("results/baseline_stats.csv"); st=pd.read_csv("results/tuned_stats.csv")
sb=sb[sb.Name!="Aggregated"]; st=st[st.Name!="Aggregated"]
fig,ax=plt.subplots(figsize=(7.2,2.6)); import numpy as np; x=np.arange(len(sb)); w=.38
ax.bar(x-w/2,sb["95%"],w,color=O,label="Baseline"); ax.bar(x+w/2,st["95%"],w,color=G,label="After tuning")
ax.set_xticks(x); ax.set_xticklabels([n[3:] for n in sb.Name],fontsize=8); ax.set_ylabel("p95 (ms)"); ax.set_title("p95 response time by transaction (whole test)",loc="left",fontsize=10,fontweight="bold"); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig("report/c4_p95_tx.png",dpi=200); plt.close(fig)
# step table
def steps(a):
    a=a.copy(); r=[]
    for u in [50,100,200,300]:
        s=a[a["User Count"]==u]; s=s.iloc[len(s)//3:]  # steady-state part of each step
        r.append((u,round(s["Requests/s"].median(),1),int(s["50%"].median()),int(s["95%"].median())))
    return r
import json; json.dump({"b":steps(b),"t":steps(t)},open("report/steps.json","w")); print(steps(b),steps(t))
